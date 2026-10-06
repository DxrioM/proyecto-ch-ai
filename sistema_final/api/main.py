"""API del Sistema Final: expone el orquestador multi-agente de forma
asincrona, con persistencia en Redis y un gate de aprobacion humana.

POST /tasks                  -> encola la tarea, devuelve job_id de inmediato (202)
GET  /tasks/{job_id}         -> estado actual (no bloquea, solo lee Redis)
POST /tasks/{job_id}/approve -> aprueba o rechaza una tarea pausada en HITL
GET  /health                 -> estado del servicio

Todas las entradas y salidas se validan con Pydantic.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..graph import compile_graph, redis_checkpointer
from ..job_store import Job, JobStatus, JobStore
from ..observability import init_observability
from ..worker import ejecutar_job, reanudar_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("sistema_final.api")

_recursos: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arma los recursos de vida larga (checkpointer de Redis, grafo
    compilado y job store) una sola vez al arrancar, y los libera al apagar."""
    init_observability()
    async with redis_checkpointer() as checkpointer:
        _recursos["graph"] = compile_graph(checkpointer)
        _recursos["job_store"] = JobStore()
        logger.info("API lista: grafo compilado, checkpointer de Redis conectado.")
        yield
    _recursos.clear()


app = FastAPI(title="Sistema Final - Intelligence System", version="1.0.0", lifespan=lifespan)


class CrearTareaRequest(BaseModel):
    """Entrada de POST /tasks."""

    pregunta: str = Field(min_length=3, max_length=1000, description="Pregunta o tarea para el sistema")


class TareaResponse(BaseModel):
    """Respuesta de POST /tasks y de POST /tasks/{id}/approve."""

    job_id: str
    status: JobStatus


class AprobacionRequest(BaseModel):
    """Entrada de POST /tasks/{id}/approve."""

    aprobado: bool = Field(default=True, description="True aprueba la accion critica, False la rechaza")


class HealthResponse(BaseModel):
    status: str


@app.post("/tasks", response_model=TareaResponse, status_code=202)
async def crear_tarea(payload: CrearTareaRequest, background_tasks: BackgroundTasks) -> TareaResponse:
    """Encola la tarea y devuelve de inmediato. El grafo corre despues de
    enviar la respuesta, en el mismo event loop."""
    job_id = str(uuid.uuid4())
    job_store: JobStore = _recursos["job_store"]
    await job_store.create(job_id, payload.pregunta)
    background_tasks.add_task(ejecutar_job, job_store, _recursos["graph"], job_id, payload.pregunta)
    return TareaResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/tasks/{job_id}", response_model=Job)
async def obtener_tarea(job_id: str) -> Job:
    """Lee el estado actual desde Redis. Si el agente fallo en segundo plano,
    el status ya es FAILED aca, no un timeout silencioso."""
    job = await _recursos["job_store"].get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return job


@app.post("/tasks/{job_id}/approve", response_model=TareaResponse)
async def aprobar_tarea(
    job_id: str, payload: AprobacionRequest, background_tasks: BackgroundTasks
) -> TareaResponse:
    """Aprueba o rechaza la accion critica pendiente de un job pausado por el
    gate Human-in-the-loop."""
    job_store: JobStore = _recursos["job_store"]
    job = await job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if job.status != JobStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=409, detail=f"El job no esta esperando aprobacion (status actual: {job.status})"
        )
    background_tasks.add_task(reanudar_job, job_store, _recursos["graph"], job_id, payload.aprobado)
    return TareaResponse(job_id=job_id, status=job.status)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
