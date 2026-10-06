"""Worker que corre el grafo en segundo plano y actualiza Redis.

Nunca deja escapar una excepcion hacia FastAPI: si el agente falla, el job
pasa a FAILED en Redis. Sin esto, un fallo en background dejaria al cliente
esperando en un loop de polling infinito.
"""

import asyncio
import logging
from typing import Any, Optional

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from .config import MAX_JOBS_CONCURRENTES, RECURSION_LIMIT
from .job_store import JobStatus, JobStore
from .observability import traced_job

logger = logging.getLogger("sistema_final.worker")

# Limita cuantos grafos corren en paralelo: cada job hace varias llamadas al
# LLM, y sin este limite una rafaga supera el TPM de la cuota de Groq (free
# tier, 8000 tokens/min). Los jobs de mas esperan en cola.
_limite_concurrencia = asyncio.Semaphore(MAX_JOBS_CONCURRENTES)


def _extraer_interrupt_payload(estado: Any) -> Optional[dict]:
    """Busca el payload de interrupt() en el ultimo PregelTask pausado."""
    for task in estado.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


async def _procesar_resultado(job_store: JobStore, job_id: str, app: Any, config: dict, resultado: dict) -> None:
    """Interpreta el resultado de un paso del grafo: si quedo pausado en un
    interrupt(), pasa a AWAITING_APPROVAL; si termino, pasa a DONE."""
    if "__interrupt__" in resultado:
        estado = await app.aget_state(config)
        payload = _extraer_interrupt_payload(estado)
        await job_store.update(job_id, status=JobStatus.AWAITING_APPROVAL, interrupt_payload=payload)
        logger.info("Job %s pausado esperando aprobacion humana", job_id)
        return

    mensajes = resultado["messages"]
    await job_store.update(
        job_id,
        status=JobStatus.DONE,
        resultado=mensajes[-1].content,
        contribuciones=resultado.get("contribuciones"),
    )
    logger.info("Job %s completado", job_id)


@traced_job
async def ejecutar_job(job_store: JobStore, app: Any, job_id: str, pregunta: str) -> None:
    """Corre el grafo desde cero para un job nuevo."""
    config = {"configurable": {"thread_id": job_id}, "recursion_limit": RECURSION_LIMIT}
    await job_store.update(job_id, status=JobStatus.RUNNING)
    try:
        async with _limite_concurrencia:
            resultado = await app.ainvoke(
                {
                    "messages": [HumanMessage(content=pregunta)],
                    "next_agent": None,
                    "task_completed": False,
                    "contribuciones": [],
                },
                config=config,
            )
        await _procesar_resultado(job_store, job_id, app, config, resultado)
    except Exception as e:
        logger.error("Job %s fallo (%s): %s", job_id, type(e).__name__, e)
        await job_store.update(job_id, status=JobStatus.FAILED, error=f"{type(e).__name__}: {e}")


async def reanudar_job(job_store: JobStore, app: Any, job_id: str, aprobado: bool) -> None:
    """Retoma un job pausado en el gate HITL, con la decision humana."""
    config = {"configurable": {"thread_id": job_id}, "recursion_limit": RECURSION_LIMIT}

    if not aprobado:
        await job_store.update(
            job_id, status=JobStatus.REJECTED, resultado="El usuario rechazo la accion critica propuesta."
        )
        logger.info("Job %s rechazado por el usuario", job_id)
        return

    await job_store.update(job_id, status=JobStatus.RUNNING)
    try:
        async with _limite_concurrencia:
            resultado = await app.ainvoke(Command(resume=True), config=config)
        await _procesar_resultado(job_store, job_id, app, config, resultado)
    except Exception as e:
        logger.error("Job %s fallo al reanudar (%s): %s", job_id, type(e).__name__, e)
        await job_store.update(job_id, status=JobStatus.FAILED, error=f"{type(e).__name__}: {e}")
