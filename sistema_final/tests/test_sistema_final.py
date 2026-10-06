"""Tests sinteticos del Sistema Final (sin Groq, Redis ni Pinecone reales).

- Validacion Pydantic de la API y de las herramientas de los agentes.
- JobStore con un cliente Redis falso (mismo contrato async de get/set).
- Flujo del grafo con Supervisor y especialistas falsos, incluida la pausa
  HITL antes del analista y su reanudacion (MemorySaver tiene la misma
  semantica de interrupt()/resume que el checkpointer de Redis).
"""

import asyncio
import math
from typing import Dict, Optional

import pytest
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import ValidationError

from sistema_final.agents.analyst import CalcularEstadisticasInput, calcular_estadisticas
from sistema_final.agents.research import BuscarEnBaseInput, buscar_en_base_de_conocimiento
from sistema_final.api.main import AprobacionRequest, CrearTareaRequest
from sistema_final.graph import compile_graph
from sistema_final.hitl import ACCION_CRITICA, construir_payload_aprobacion
from sistema_final.job_store import JobStatus, JobStore
from sistema_final.supervisor import SupervisorDecision
from sistema_final.worker import ejecutar_job, reanudar_job

# ---------------------------------------------------------------------------
# 1. Validacion Pydantic (API y herramientas)
# ---------------------------------------------------------------------------


def test_api_rechaza_pregunta_demasiado_corta():
    with pytest.raises(ValidationError):
        CrearTareaRequest(pregunta="ab")


def test_api_rechaza_pregunta_demasiado_larga():
    with pytest.raises(ValidationError):
        CrearTareaRequest(pregunta="x" * 1001)


def test_api_acepta_pregunta_valida_y_aprobado_por_defecto():
    assert CrearTareaRequest(pregunta="Que base de datos usa el sistema?").pregunta.startswith("Que")
    assert AprobacionRequest().aprobado is True


def test_herramienta_investigacion_rechaza_consulta_corta_antes_de_buscar():
    with pytest.raises(ValidationError):
        BuscarEnBaseInput(query="a")


def test_herramienta_calculo_rechaza_lista_vacia():
    with pytest.raises(ValidationError):
        CalcularEstadisticasInput(valores=[])


def test_herramienta_calculo_rechaza_valores_no_finitos():
    with pytest.raises(ValidationError):
        CalcularEstadisticasInput(valores=[1.0, math.nan])


def test_herramienta_calculo_devuelve_estadisticas():
    resultado = calcular_estadisticas.invoke({"valores": [2.0, 4.0, 6.0]})

    assert resultado["promedio"] == 4.0
    assert resultado["minimo"] == 2.0
    assert resultado["maximo"] == 6.0
    assert resultado["cantidad"] == 3


def test_herramienta_investigacion_tiene_schema_con_query():
    assert "query" in buscar_en_base_de_conocimiento.args


# ---------------------------------------------------------------------------
# 2. HITL
# ---------------------------------------------------------------------------


def test_construir_payload_aprobacion():
    payload = construir_payload_aprobacion("pregunta original", "hallazgos del investigador")

    assert payload["accion"] == ACCION_CRITICA
    assert payload["pregunta_original"] == "pregunta original"
    assert payload["datos_investigados"] == "hallazgos del investigador"


# ---------------------------------------------------------------------------
# 3. JobStore (con un cliente Redis falso)
# ---------------------------------------------------------------------------


class _FakeRedis:
    """Doble falso con el mismo contrato async que redis.asyncio.Redis."""

    def __init__(self):
        self._data: Dict[str, str] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        self._data[key] = value


def test_job_store_create_get_y_update_conservan_campos():
    store = JobStore(redis_client=_FakeRedis())
    asyncio.run(store.create("job-1", "otra pregunta"))

    actualizado = asyncio.run(store.update("job-1", status=JobStatus.DONE, resultado="42"))

    assert actualizado.status == JobStatus.DONE
    assert actualizado.pregunta == "otra pregunta"
    assert asyncio.run(store.get("job-1")).resultado == "42"


def test_job_store_get_inexistente_devuelve_none():
    assert asyncio.run(JobStore(redis_client=_FakeRedis()).get("no-existe")) is None


# ---------------------------------------------------------------------------
# 4. Grafo completo con Supervisor y especialistas falsos
# ---------------------------------------------------------------------------


class _FakeSupervisor:
    """Entrega una secuencia fija de decisiones, una por llamada."""

    def __init__(self, decisiones):
        self._decisiones = list(decisiones)
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        return self._decisiones.pop(0)


class _FakeEspecialista:
    def __init__(self, respuesta: str):
        self.respuesta = respuesta
        self.calls = 0

    async def ainvoke(self, _input):
        self.calls += 1
        return {"messages": [AIMessage(content=self.respuesta)]}


def _app(decisiones, investigador=None, analista=None):
    return compile_graph(
        checkpointer=MemorySaver(),
        supervisor_model=_FakeSupervisor(decisiones),
        research_agent=investigador or _FakeEspecialista("hallazgo: el sistema usa PostgreSQL"),
        analyst_agent=analista or _FakeEspecialista("calculo: promedio 42"),
    )


def test_job_sin_calculo_termina_done_sin_pasar_por_hitl():
    store = JobStore(redis_client=_FakeRedis())
    app = _app([SupervisorDecision(next_agent="FINISH", razon="listo", respuesta_final="Listo.")])
    asyncio.run(store.create("job-simple", "pregunta simple"))

    asyncio.run(ejecutar_job(store, app, "job-simple", "pregunta simple"))

    job = asyncio.run(store.get("job-simple"))
    assert job.status == JobStatus.DONE
    assert job.resultado == "Listo."


def test_job_investigador_y_luego_finish_registra_la_contribucion():
    store = JobStore(redis_client=_FakeRedis())
    app = _app(
        [
            SupervisorDecision(next_agent="investigador", razon="falta informacion"),
            SupervisorDecision(next_agent="FINISH", razon="ya alcanza", respuesta_final="Usa PostgreSQL."),
        ]
    )
    asyncio.run(store.create("job-inv", "que base de datos usa"))

    asyncio.run(ejecutar_job(store, app, "job-inv", "que base de datos usa"))

    job = asyncio.run(store.get("job-inv"))
    assert job.status == JobStatus.DONE
    assert [c["agente"] for c in job.contribuciones] == ["investigador"]


def test_job_con_calculo_queda_pausado_en_hitl_y_al_aprobar_completa():
    store = JobStore(redis_client=_FakeRedis())
    app = _app(
        [
            SupervisorDecision(next_agent="analista", razon="hace falta calcular"),
            SupervisorDecision(next_agent="FINISH", razon="listo", respuesta_final="Resultado final: 42"),
        ]
    )
    asyncio.run(store.create("job-hitl", "pregunta con calculo"))

    asyncio.run(ejecutar_job(store, app, "job-hitl", "pregunta con calculo"))
    pausado = asyncio.run(store.get("job-hitl"))
    assert pausado.status == JobStatus.AWAITING_APPROVAL
    assert pausado.interrupt_payload["accion"] == ACCION_CRITICA

    asyncio.run(reanudar_job(store, app, "job-hitl", aprobado=True))
    final = asyncio.run(store.get("job-hitl"))
    assert final.status == JobStatus.DONE
    assert final.resultado == "Resultado final: 42"


def test_job_con_calculo_rechazado_no_ejecuta_el_analista():
    store = JobStore(redis_client=_FakeRedis())
    analista = _FakeEspecialista("calculo que no debe correr")
    app = _app([SupervisorDecision(next_agent="analista", razon="calcular")], analista=analista)
    asyncio.run(store.create("job-rech", "pregunta con calculo"))
    asyncio.run(ejecutar_job(store, app, "job-rech", "pregunta con calculo"))

    asyncio.run(reanudar_job(store, app, "job-rech", aprobado=False))

    assert asyncio.run(store.get("job-rech")).status == JobStatus.REJECTED
    assert analista.calls == 0


def test_excepcion_del_agente_deja_el_job_failed_sin_crashear():
    class _SupervisorRoto:
        async def ainvoke(self, messages):
            raise ConnectionError("fallo de red simulado")

    store = JobStore(redis_client=_FakeRedis())
    app = compile_graph(
        checkpointer=MemorySaver(),
        supervisor_model=_SupervisorRoto(),
        research_agent=_FakeEspecialista("x"),
        analyst_agent=_FakeEspecialista("y"),
    )
    asyncio.run(store.create("job-failed", "pregunta cualquiera"))

    asyncio.run(ejecutar_job(store, app, "job-failed", "pregunta cualquiera"))

    job = asyncio.run(store.get("job-failed"))
    assert job.status == JobStatus.FAILED
    assert "ConnectionError" in job.error
