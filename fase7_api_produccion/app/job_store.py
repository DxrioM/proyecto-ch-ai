"""Fase 7: estado de los jobs persistido en Redis.

Cada job (una pregunta encolada contra el orquestador) se guarda como un
JSON serializado bajo la clave `job:{job_id}`, con un TTL para no acumular
jobs viejos indefinidamente. Esto es lo que permite que GET /tasks/{id} no
bloquee: el endpoint solo lee el estado ya calculado en Redis, nunca espera
a que el agente termine.
"""

import json
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from redis.asyncio import Redis

JOB_TTL_SECONDS = 24 * 60 * 60  # 24hs: suficiente para debug, no acumula para siempre


class JobStatus(str, Enum):
    """Estados posibles de un job. FAILED es critico: si el agente explota
    en background, el cliente no debe quedarse esperando en un loop de
    polling infinito - el estado SIEMPRE debe llegar a un estado terminal
    (DONE, FAILED o REJECTED)."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    DONE = "DONE"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class Job(BaseModel):
    """Estado completo de un job, tal como se persiste en Redis."""

    job_id: str
    pregunta: str
    status: JobStatus = JobStatus.PENDING
    creado_en: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actualizado_en: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resultado: Optional[str] = None
    error: Optional[str] = None
    interrupt_payload: Optional[Dict[str, Any]] = None
    contribuciones: Optional[list] = None


def _redis_client() -> Redis:
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        raise ValueError("Falta REDIS_URL en .env")
    return Redis.from_url(redis_url, decode_responses=True)


class JobStore:
    """Encapsula las operaciones de Redis sobre jobs. Inyectable (recibe un
    cliente redis ya armado) para poder testear con un doble falso sin
    depender de una conexion real."""

    def __init__(self, redis_client: Optional[Redis] = None):
        self._redis = redis_client or _redis_client()

    @staticmethod
    def _key(job_id: str) -> str:
        return f"job:{job_id}"

    async def create(self, job_id: str, pregunta: str) -> Job:
        job = Job(job_id=job_id, pregunta=pregunta, status=JobStatus.PENDING)
        await self._save(job)
        return job

    async def get(self, job_id: str) -> Optional[Job]:
        raw = await self._redis.get(self._key(job_id))
        if raw is None:
            return None
        return Job.model_validate_json(raw)

    async def update(self, job_id: str, **campos: Any) -> Job:
        job = await self.get(job_id)
        if job is None:
            raise KeyError(f"No existe el job {job_id}")
        actualizado = job.model_copy(update={**campos, "actualizado_en": datetime.now(timezone.utc).isoformat()})
        await self._save(actualizado)
        return actualizado

    async def _save(self, job: Job) -> None:
        await self._redis.set(self._key(job.job_id), job.model_dump_json(), ex=JOB_TTL_SECONDS)
