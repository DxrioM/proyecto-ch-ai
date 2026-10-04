"""Tests sinteticos para la Fase 6 (orquestador multi-agente con Supervisor).

1. Herramientas: deterministas, sin LLM.
2. Flujo de delegacion del grafo: con un Supervisor falso (decisiones
   prefijadas) y agentes especialistas falsos (sin create_react_agent real
   ni LLM real), para probar el RUTEO del Supervisor y el registro de
   contribuciones de forma determinista, sin gastar cuota de Groq.
"""

import asyncio
from typing import List

from langchain_core.messages import AIMessage, HumanMessage

from fase6_orquestador_multiagente.agents.analyst_agent import calcular_estadisticas
from fase6_orquestador_multiagente.graph import SupervisorDecision, compile_graph

# ---------------------------------------------------------------------------
# 1. Herramientas
# ---------------------------------------------------------------------------


def test_calcular_estadisticas_valores_normales():
    resultado = calcular_estadisticas.invoke({"valores": [0.5, 4.0, 16.0]})

    assert resultado["promedio"] == 20.5 / 3
    assert resultado["minimo"] == 0.5
    assert resultado["maximo"] == 16.0
    assert resultado["cantidad"] == 3


def test_calcular_estadisticas_lista_vacia_devuelve_error_sin_crashear():
    resultado = calcular_estadisticas.invoke({"valores": []})

    assert "error" in resultado


# ---------------------------------------------------------------------------
# 2. Flujo de delegacion del grafo (Supervisor + especialistas falsos)
# ---------------------------------------------------------------------------


class _FakeSupervisor:
    """Devuelve una secuencia prefijada de decisiones, una por llamada."""

    def __init__(self, decisiones: List[SupervisorDecision]):
        self._decisiones = list(decisiones)
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        return self._decisiones.pop(0)


class _FakeSpecialistAgent:
    """Reemplaza un especialista entero (bypassea create_react_agent y el
    LLM real): siempre responde con un texto fijo."""

    def __init__(self, respuesta: str):
        self.respuesta = respuesta
        self.calls = 0

    async def ainvoke(self, input_):
        self.calls += 1
        return {"messages": [AIMessage(content=self.respuesta)]}


def test_graph_full_delegation_flow_investigador_then_analista_then_finish():
    fake_supervisor = _FakeSupervisor(
        [
            SupervisorDecision(next_agent="investigador", razon="falta info"),
            SupervisorDecision(next_agent="analista", razon="ya hay info, falta calcular"),
            SupervisorDecision(
                next_agent="FINISH", razon="listo", respuesta_final="El promedio es 6.83 horas."
            ),
        ]
    )
    fake_research = _FakeSpecialistAgent("SLA: severidad 1 = 0.5h, severidad 2 = 4h, severidad 3 = 16h")
    fake_analyst = _FakeSpecialistAgent("El promedio de 0.5, 4 y 16 es 6.83 horas")

    app = compile_graph(
        supervisor_model=fake_supervisor, research_agent=fake_research, analyst_agent=fake_analyst
    )

    resultado = asyncio.run(
        app.ainvoke(
            {
                "messages": [HumanMessage(content="pregunta de prueba")],
                "next_agent": None,
                "task_completed": False,
                "contribuciones": [],
            }
        )
    )

    assert resultado["task_completed"] is True
    assert resultado["messages"][-1].content == "El promedio es 6.83 horas."
    assert fake_supervisor.calls == 3
    assert fake_research.calls == 1
    assert fake_analyst.calls == 1

    # Las contribuciones quedan registradas en orden, una por especialista -
    # asi es como el sistema evita "perder el contexto" de quien aporto que.
    agentes = [c["agente"] for c in resultado["contribuciones"]]
    assert agentes == ["investigador", "analista"]


def test_graph_skips_specialists_when_supervisor_finishes_immediately():
    fake_supervisor = _FakeSupervisor(
        [SupervisorDecision(next_agent="FINISH", razon="no hace falta nada mas", respuesta_final="Listo.")]
    )
    fake_research = _FakeSpecialistAgent("no deberia llamarse")
    fake_analyst = _FakeSpecialistAgent("no deberia llamarse")

    app = compile_graph(
        supervisor_model=fake_supervisor, research_agent=fake_research, analyst_agent=fake_analyst
    )

    resultado = asyncio.run(
        app.ainvoke(
            {
                "messages": [HumanMessage(content="pregunta de prueba")],
                "next_agent": None,
                "task_completed": False,
                "contribuciones": [],
            }
        )
    )

    assert resultado["messages"][-1].content == "Listo."
    assert fake_research.calls == 0
    assert fake_analyst.calls == 0


def test_graph_strict_sufficiency_cutoff_forces_finish_without_extra_llm_call():
    """El Supervisor Infinito que advierte la consigna: si un Supervisor
    (real o con un bug) nunca decide FINISH por si solo, el criterio de
    suficiencia estricto (MAX_CONTRIBUCIONES) debe cortar el ciclo igual,
    sin siquiera llamar al LLM del Supervisor una vez mas."""
    # Siempre pide al investigador, nunca termina por si solo.
    decisiones = [SupervisorDecision(next_agent="investigador", razon="pide de nuevo") for _ in range(10)]
    fake_supervisor = _FakeSupervisor(decisiones)
    fake_research = _FakeSpecialistAgent("dato parcial")
    fake_analyst = _FakeSpecialistAgent("no deberia llamarse")

    app = compile_graph(
        supervisor_model=fake_supervisor, research_agent=fake_research, analyst_agent=fake_analyst
    )

    resultado = asyncio.run(
        app.ainvoke(
            {
                "messages": [HumanMessage(content="pregunta de prueba")],
                "next_agent": None,
                "task_completed": False,
                "contribuciones": [],
            },
            config={"recursion_limit": 25},
        )
    )

    assert resultado["task_completed"] is True
    # 4 decisiones reales del supervisor (MAX_CONTRIBUCIONES) y en la 5ta
    # invocacion del nodo el corte estricto actua ANTES de llamar al LLM.
    assert fake_supervisor.calls == 4
    assert fake_analyst.calls == 0
