"""Orquestador multi-agente: un nodo Supervisor decide en cada paso si
intervienen el Investigador, el Analista, o si la tarea esta completa
(FINISH, con una sintesis final).

La decision se mapea a una arista condicional via un campo Literal
(next_agent), nunca con un if/else fijo que ignore el contenido real de la
conversacion. El punto HITL (hitl_gate) se llama al principio del nodo
Analista, antes de cualquier calculo.
"""

import logging
from typing import Any, Callable, List, Literal, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from sistema_final.agents.analyst import build_analyst_agent
from sistema_final.agents.research import build_research_agent
from sistema_final.config import GROQ_MODEL, get_required
from sistema_final.state import Contribucion, OrchestratorState

logger = logging.getLogger("sistema_final.supervisor")

# Criterio de suficiencia estricto: si ya se acumularon demasiadas
# contribuciones sin que el Supervisor decida terminar, se fuerza el cierre.
MAX_CONTRIBUCIONES = 4

SUPERVISOR_PROMPT = """Sos el Supervisor de un sistema multi-agente de analisis e investigacion.
Tenes dos especialistas disponibles:
- investigador: busca informacion en la base de conocimiento vectorial. Usalo cuando falte informacion factual/documentada.
- analista: hace calculos matematicos sobre datos ya investigados (promedios, min/max, etc). Usalo cuando ya haya datos numericos para procesar pero todavia no se hayan calculado.

Contribuciones ya recibidas en esta tarea:
{contribuciones}

Decidi UNA de estas tres opciones:
- "investigador": si todavia falta informacion factual para responder la pregunta del usuario.
- "analista": si ya hay datos suficientes investigados pero falta procesarlos/calcularlos.
- "FINISH": si la tarea ya esta completa (ya se investigo Y se analizo lo necesario, o la pregunta no requeria ambos pasos). Cuando elijas FINISH, escribi tambien la respuesta final completa para el usuario en "respuesta_final", sintetizando lo que aportaron los especialistas.

REGLA ESTRICTA: vos (el Supervisor) NUNCA haces calculos matematicos ni conversiones de unidades, ni siquiera en "respuesta_final" - eso es trabajo EXCLUSIVO del analista. Si la pregunta original del usuario pide una operacion matematica (promedio, suma, conversion de unidades, etc.) sobre datos que trajo el investigador, rutea SIEMPRE al menos una vez al analista antes de poder elegir FINISH, incluso si el calculo te parece trivial. Tu "respuesta_final" solo puede repetir numeros que el analista ya calculo explicitamente, nunca numeros que calculaste vos.

Criterio de suficiencia: no le pidas a un especialista que repita un trabajo que ya hizo correctamente. Si investigador y analista ya contribuyeron una vez cada uno con resultados utiles, preferi FINISH."""


class SupervisorDecision(BaseModel):
    """Salida estructurada del Supervisor, validada con Pydantic."""

    next_agent: Literal["investigador", "analista", "FINISH"] = Field(
        description="A que especialista rutear a continuacion, o FINISH si la tarea ya esta completa"
    )
    razon: str = Field(description="Breve justificacion de la decision, en espanol")
    respuesta_final: Optional[str] = Field(
        default=None,
        description="Solo si next_agent es FINISH: la sintesis final para el usuario, combinando los aportes de los especialistas",
    )


def build_supervisor_model():
    """Modelo de Groq con salida estructurada. El nombre del modelo sale de
    la configuracion (GROQ_MODEL) y los reintentos cubren el rate limit."""
    model = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        api_key=get_required("GROQ_API_KEY"),
        max_retries=8,
    )
    return model.with_structured_output(SupervisorDecision)


def build_specialist_model():
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        api_key=get_required("GROQ_API_KEY"),
        max_retries=8,
    )


def _formatear_contribuciones(contribuciones: List[Contribucion]) -> str:
    if not contribuciones:
        return "(ninguna todavia)"
    return "\n".join(f"- {c['agente']}: {c['resumen']}" for c in contribuciones)


def _ultima_instruccion(messages: List[BaseMessage]) -> str:
    """Devuelve solo la pregunta original del usuario para pasarla a un
    especialista, en vez de todo el historial interno (evita contaminar el
    contexto del especialista con mensajes de otros agentes)."""
    for m in messages:
        if isinstance(m, HumanMessage):
            return m.content
    return messages[-1].content if messages else ""


def build_graph(
    supervisor_model: Optional[Any] = None,
    research_model: Optional[Any] = None,
    analyst_model: Optional[Any] = None,
    research_agent: Optional[Any] = None,
    analyst_agent: Optional[Any] = None,
    hitl_gate: Optional[Callable[[OrchestratorState], None]] = None,
) -> StateGraph:
    """Arma el grafo sin compilar.

    Inyectable en dos niveles para poder testear sin Groq real:
    *_model reemplaza solo el LLM (sigue pasando por create_react_agent);
    research_agent/analyst_agent reemplazan al especialista entero (cualquier
    objeto con .ainvoke). hitl_gate, si se pasa, se llama al principio del
    nodo analista y puede pausar el grafo con interrupt().
    """
    supervisor_structured_model = supervisor_model or build_supervisor_model()
    research_agent = research_agent or build_research_agent(research_model or build_specialist_model())
    analyst_agent = analyst_agent or build_analyst_agent(analyst_model or build_specialist_model())

    async def supervisor_node(state: OrchestratorState) -> dict:
        contribuciones = state.get("contribuciones", [])

        if len(contribuciones) >= MAX_CONTRIBUCIONES:
            logger.info("Criterio de suficiencia alcanzado (%d contribuciones): forzando FINISH", len(contribuciones))
            sintesis = "Resumen de lo investigado y analizado hasta ahora:\n" + _formatear_contribuciones(contribuciones)
            return {
                "next_agent": "FINISH",
                "task_completed": True,
                "messages": [AIMessage(content=sintesis, name="supervisor")],
            }

        prompt = SUPERVISOR_PROMPT.format(contribuciones=_formatear_contribuciones(contribuciones))
        mensajes = [SystemMessage(content=prompt)] + state["messages"]
        decision = await supervisor_structured_model.ainvoke(mensajes)
        logger.info("Supervisor decide: %s (%s)", decision.next_agent, decision.razon)

        update: dict = {"next_agent": decision.next_agent}
        if decision.next_agent == "FINISH":
            update["task_completed"] = True
            update["messages"] = [AIMessage(content=decision.respuesta_final or decision.razon, name="supervisor")]
        return update

    async def investigador_node(state: OrchestratorState) -> dict:
        instruccion = _ultima_instruccion(state["messages"])
        resultado = await research_agent.ainvoke({"messages": [HumanMessage(content=instruccion)]})
        texto = resultado["messages"][-1].content
        logger.info("Investigador aporta: %s", texto[:150])
        return {
            "messages": [AIMessage(content=texto, name="investigador")],
            # El resumen NO se trunca: el Supervisor lo usa para decidir si la
            # informacion esta completa. Un recorte corta tablas a mitad.
            "contribuciones": [Contribucion(agente="investigador", resumen=texto)],
        }

    async def analista_node(state: OrchestratorState) -> dict:
        if hitl_gate is not None:
            # Pausa el grafo antes de cualquier trabajo real. Al reanudar,
            # interrupt() no vuelve a pausar (el replay es idempotente).
            hitl_gate(state)
        instruccion = _ultima_instruccion(state["messages"])
        hallazgos = "\n".join(
            c["resumen"] for c in state.get("contribuciones", []) if c["agente"] == "investigador"
        )
        contenido = f"{instruccion}\n\nDatos investigados disponibles:\n{hallazgos}" if hallazgos else instruccion
        resultado = await analyst_agent.ainvoke({"messages": [HumanMessage(content=contenido)]})
        texto = resultado["messages"][-1].content
        logger.info("Analista aporta: %s", texto[:150])
        return {
            "messages": [AIMessage(content=texto, name="analista")],
            "contribuciones": [Contribucion(agente="analista", resumen=texto)],
        }

    def route_supervisor(state: OrchestratorState) -> Literal["investigador", "analista", "__end__"]:
        next_agent = state.get("next_agent")
        if next_agent in ("investigador", "analista"):
            return next_agent
        return "__end__"

    graph = StateGraph(OrchestratorState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("investigador", investigador_node)
    graph.add_node("analista", analista_node)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor", route_supervisor, {"investigador": "investigador", "analista": "analista", "__end__": END}
    )
    graph.add_edge("investigador", "supervisor")
    graph.add_edge("analista", "supervisor")
    return graph
