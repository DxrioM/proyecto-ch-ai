"""Tests sinteticos para la Fase 7 (API de produccion, Redis, HITL).

No requieren un Redis real ni la API de Groq real:
- JobStore se prueba con un cliente Redis falso (mismo contrato async que
  redis.asyncio.Redis: get/set), para probar la logica de serializacion
  sin una conexion real.
- El flujo completo del grafo (incluida la pausa HITL) se prueba con
  MemorySaver - tiene exactamente la misma semantica de interrupt()/resume
  que AsyncRedisSaver (verificado manualmente antes de escribir worker.py:
  ambos son Checkpointer de LangGraph, el contrato es identico), y
  Supervisor/especialistas falsos, igual que en tests/test_fase6_orchestrator.py.
"""

import asyncio
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from fase6_orquestador_multiagente.graph import SupervisorDecision
from fase7_api_produccion.app.graph import compile_graph
from fase7_api_produccion.app.hitl import ACCION_CRITICA, construir_payload_aprobacion
from fase7_api_produccion.app.job_store import Job, JobStatus, JobStore
from fase7_api_produccion.app.worker import ejecutar_job, reanudar_job

# ---------------------------------------------------------------------------
# 1. hitl.py
# ---------------------------------------------------------------------------


def test_construir_payload_aprobacion():
    payload = construir_payload_aprobacion("pregunta original", "hallazgos del investigador")

    assert payload["accion"] == ACCION_CRITICA
    assert payload["pregunta_original"] == "pregunta original"
    assert payload["datos_investigados"] == "hallazgos del investigador"
    assert "motivo" in payload


# ---------------------------------------------------------------------------
# 2. JobStore (con un cliente Redis falso)
# ---------------------------------------------------------------------------


class _FakeRedis:
    """Doble falso con el mismo contrato async que redis.asyncio.Redis
    (get/set), respaldado por un dict en memoria."""

    def __init__(self):
        self._data: Dict[str, str] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        self._data[key] = value


def test_job_store_create_and_get():
    store = JobStore(redis_client=_FakeRedis())

    job = asyncio.run(store.create("job-1", "una pregunta"))

    assert job.status == JobStatus.PENDING
    recuperado = asyncio.run(store.get("job-1"))
    assert recuperado is not None
    assert recuperado.pregunta == "una pregunta"


def test_job_store_get_nonexistent_returns_none():
    store = JobStore(redis_client=_FakeRedis())

    assert asyncio.run(store.get("no-existe")) is None


def test_job_store_update_merges_fields():
    store = JobStore(redis_client=_FakeRedis())
    asyncio.run(store.create("job-2", "otra pregunta"))

    actualizado = asyncio.run(store.update("job-2", status=JobStatus.DONE, resultado="42"))

    assert actualizado.status == JobStatus.DONE
    assert actualizado.resultado == "42"
    assert actualizado.pregunta == "otra pregunta"  # no se pierde al actualizar solo 2 campos


def test_job_store_update_nonexistent_raises():
    store = JobStore(redis_client=_FakeRedis())

    try:
        asyncio.run(store.update("no-existe", status=JobStatus.DONE))
        assert False, "deberia haber lanzado KeyError"
    except KeyError:
        pass


# ---------------------------------------------------------------------------
# 3. Flujo completo del worker: ejecutar_job + reanudar_job, con el gate HITL
# ---------------------------------------------------------------------------


class _FakeSupervisorRoutesToAnalista:
    """Siempre pide al analista - fuerza el camino que pasa por el gate HITL."""

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            return SupervisorDecision(next_agent="analista", razon="hace falta calcular")
        return SupervisorDecision(next_agent="FINISH", razon="listo", respuesta_final="Resultado final: 42")


class _FakeSupervisorNeverNeedsAnalista:
    """Nunca pide al analista - el gate HITL nunca deberia dispararse."""

    async def ainvoke(self, messages):
        return SupervisorDecision(next_agent="FINISH", razon="no hace falta nada mas", respuesta_final="Listo.")


class _FakeSpecialistAgent:
    def __init__(self, respuesta: str):
        self.respuesta = respuesta
        self.calls = 0

    async def ainvoke(self, input_):
        self.calls += 1
        return {"messages": [AIMessage(content=self.respuesta)]}


def _build_app(supervisor_model):
    return compile_graph(
        checkpointer=MemorySaver(),
        supervisor_model=supervisor_model,
        research_agent=_FakeSpecialistAgent("hallazgo del investigador"),
        analyst_agent=_FakeSpecialistAgent("calculo del analista"),
    )


def test_ejecutar_job_sin_hitl_llega_a_done():
    """Si el Supervisor nunca rutea al analista, el job nunca pasa por el
    gate HITL y termina DONE en una sola corrida."""
    store = JobStore(redis_client=_FakeRedis())
    app = _build_app(_FakeSupervisorNeverNeedsAnalista())
    asyncio.run(store.create("job-done", "pregunta simple"))

    asyncio.run(ejecutar_job(store, app, "job-done", "pregunta simple"))

    job = asyncio.run(store.get("job-done"))
    assert job.status == JobStatus.DONE
    assert job.resultado == "Listo."


def test_ejecutar_job_con_hitl_queda_awaiting_approval():
    """Si el Supervisor rutea al analista, el gate HITL pausa el grafo y el
    job queda AWAITING_APPROVAL, con el payload de la decision disponible."""
    store = JobStore(redis_client=_FakeRedis())
    app = _build_app(_FakeSupervisorRoutesToAnalista())
    asyncio.run(store.create("job-hitl", "pregunta que requiere calculo"))

    asyncio.run(ejecutar_job(store, app, "job-hitl", "pregunta que requiere calculo"))

    job = asyncio.run(store.get("job-hitl"))
    assert job.status == JobStatus.AWAITING_APPROVAL
    assert job.interrupt_payload is not None
    assert job.interrupt_payload["accion"] == ACCION_CRITICA


def test_reanudar_job_aprobado_completa_la_tarea():
    store = JobStore(redis_client=_FakeRedis())
    app = _build_app(_FakeSupervisorRoutesToAnalista())
    asyncio.run(store.create("job-aprobado", "pregunta que requiere calculo"))
    asyncio.run(ejecutar_job(store, app, "job-aprobado", "pregunta que requiere calculo"))
    assert asyncio.run(store.get("job-aprobado")).status == JobStatus.AWAITING_APPROVAL

    asyncio.run(reanudar_job(store, app, "job-aprobado", aprobado=True))

    job = asyncio.run(store.get("job-aprobado"))
    assert job.status == JobStatus.DONE
    assert job.resultado == "Resultado final: 42"
    # _FakeSupervisorRoutesToAnalista rutea directo a "analista" desde el
    # primer paso (sin pasar por "investigador" primero) - el flujo
    # investigador->analista completo ya esta cubierto por los tests de la
    # Fase 6; esto solo verifica que reanudar_job() complete la tarea.
    agentes = [c["agente"] for c in job.contribuciones]
    assert agentes == ["analista"]


def test_reanudar_job_rechazado_no_ejecuta_el_analista():
    store = JobStore(redis_client=_FakeRedis())
    supervisor = _FakeSupervisorRoutesToAnalista()
    app = _build_app(supervisor)
    asyncio.run(store.create("job-rechazado", "pregunta que requiere calculo"))
    asyncio.run(ejecutar_job(store, app, "job-rechazado", "pregunta que requiere calculo"))

    asyncio.run(reanudar_job(store, app, "job-rechazado", aprobado=False))

    job = asyncio.run(store.get("job-rechazado"))
    assert job.status == JobStatus.REJECTED
    # El supervisor solo fue llamado 1 vez (la decision inicial); nunca se
    # le pidio una sintesis final porque el analista nunca corrio.
    assert supervisor.calls == 1


def test_ejecutar_job_con_excepcion_queda_failed_sin_crashear():
    """Si el agente explota, el job pasa a FAILED en vez de dejar al
    cliente esperando en un loop de polling infinito."""

    class _FakeSupervisorRoto:
        async def ainvoke(self, messages):
            raise ConnectionError("fallo de red simulado")

    store = JobStore(redis_client=_FakeRedis())
    app = _build_app(_FakeSupervisorRoto())
    asyncio.run(store.create("job-failed", "pregunta cualquiera"))

    # No debe lanzar - ejecutar_job atrapa la excepcion internamente.
    asyncio.run(ejecutar_job(store, app, "job-failed", "pregunta cualquiera"))

    job = asyncio.run(store.get("job-failed"))
    assert job.status == JobStatus.FAILED
    assert "ConnectionError" in job.error
