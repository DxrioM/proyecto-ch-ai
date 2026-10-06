"""Fase 6: grafo del orquestador multi-agente (topologia jerarquica).

Un nodo Supervisor actua como router inteligente: en cada paso decide, en
base a la conversacion y a lo que ya aportaron los especialistas, si debe
intervenir el Investigador, el Analista, o si la tarea esta completa
(FINISH, con una sintesis final). La decision se mapea a una arista
condicional via un campo Literal (next_agent) - nunca un if/else fijo que
ignore el contenido real de la conversacion.
"""

import logging
import os
from typing import Any, Callable, List, Literal, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from .agents.analyst_agent import build_analyst_agent
from .agents.research_agent import build_research_agent
from .state import Contribucion, OrchestratorState

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("fase6_supervisor")

# Criterio de suficiencia ESTRICTO (ademas del recursion_limit externo):
# si ya se acumularon demasiadas contribuciones sin que el supervisor haya
# decidido terminar, se fuerza el cierre. Evita el "Supervisor Infinito"
# que advierte la consigna.
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
    """Salida estructurada del Supervisor: a quien rutear, por que, y -solo
    si ya termino- la sintesis final para el usuario."""

    next_agent: Literal["investigador", "analista", "FINISH"] = Field(
        description="A que especialista rutear a continuacion, o FINISH si la tarea ya esta completa"
    )
    razon: str = Field(description="Breve justificacion de la decision, en espanol")
    respuesta_final: Optional[str] = Field(
        default=None,
        description="Solo si next_agent es FINISH: la sintesis final para el usuario, combinando los aportes de los especialistas",
    )


def _build_supervisor_model():
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Falta GROQ_API_KEY en .env")
    model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key, max_retries=8)
    return model.with_structured_output(SupervisorDecision)


def _build_specialist_model():
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Falta GROQ_API_KEY en .env")
    return ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key, max_retries=8)


def _formatear_contribuciones(contribuciones: List[Contribucion]) -> str:
    if not contribuciones:
        return "(ninguna todavia)"
    return "\n".join(f"- {c['agente']}: {c['resumen']}" for c in contribuciones)


def _ultima_instruccion(messages: List[BaseMessage]) -> str:
    """Extrae la instruccion mas relevante para pasarle a un especialista,
    en vez de todo el historial completo.

    Evita la "Contaminacion de Contexto" que advierte la consigna: el
    especialista no necesita ver todo el estado interno del sistema (los
    mensajes del supervisor, las tool calls de otros agentes), solo la
    pregunta original del usuario.
    """
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
    """Arma el grafo (sin compilar).

    Inyectable en dos niveles, para poder testear sin depender de la API
    real de Groq: *_model reemplaza solo el LLM subyacente (sigue pasando
    por create_react_agent de verdad); research_agent/analyst_agent
    reemplaza el especialista entero (un objeto con .ainvoke(...) propio),
    para testear el ruteo del Supervisor sin ejecutar ningun ciclo ReAct
    real.

    hitl_gate es un punto de extension para la Fase 7 (API de produccion):
    si se pasa, se llama al principio del nodo 'analista', antes de hacer
    cualquier trabajo real - la Fase 7 lo usa para pausar el grafo
    (langgraph.types.interrupt) y esperar aprobacion humana. La Fase 6 no
    necesita saber nada de interrupt()/HITL; default None preserva el
    comportamiento exacto de la Fase 6."""
    supervisor_structured_model = supervisor_model or _build_supervisor_model()
    research_agent = research_agent or build_research_agent(research_model or _build_specialist_model())
    analyst_agent = analyst_agent or build_analyst_agent(analyst_model or _build_specialist_model())

    async def supervisor_node(state: OrchestratorState) -> dict:
        contribuciones = state.get("contribuciones", [])

        if len(contribuciones) >= MAX_CONTRIBUCIONES:
            logger.info("Criterio de suficiencia estricto alcanzado (%d contribuciones): forzando FINISH", len(contribuciones))
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
            update["messages"] = [
                AIMessage(content=decision.respuesta_final or decision.razon, name="supervisor")
            ]
        return update

    async def investigador_node(state: OrchestratorState) -> dict:
        instruccion = _ultima_instruccion(state["messages"])
        resultado = await research_agent.ainvoke({"messages": [HumanMessage(content=instruccion)]})
        texto = resultado["messages"][-1].content
        logger.info("Investigador aporta: %s", texto[:150])
        return {
            "messages": [AIMessage(content=texto, name="investigador")],
            # El resumen NO se trunca: el Supervisor lo usa como fuente
            # principal para decidir si la informacion esta completa. Un
            # recorte agresivo (ej. texto[:300]) corta tablas/listas a
            # mitad y hace que el Supervisor crea que falta informacion
            # que en realidad ya esta - el sintoma real observado fue un
            # bucle de 3-4 llamadas extra al investigador por esto.
            "contribuciones": [Contribucion(agente="investigador", resumen=texto)],
        }

    async def analista_node(state: OrchestratorState) -> dict:
        if hitl_gate is not None:
            # Pausa el grafo (si hitl_gate llama a interrupt()) antes de
            # hacer cualquier trabajo real. Si el grafo se reanuda despues
            # de una pausa, esta llamada es un no-op (interrupt() no
            # vuelve a pausar en el replay).
            hitl_gate(state)
        instruccion = _ultima_instruccion(state["messages"])
        # El analista SI necesita ver lo que encontro el investigador (no
        # solo la pregunta original), asi que se lo agregamos a su
        # instruccion puntual - sigue siendo contexto acotado, no el
        # historial completo del sistema.
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


def compile_graph(
    supervisor_model: Optional[Any] = None,
    research_model: Optional[Any] = None,
    analyst_model: Optional[Any] = None,
    research_agent: Optional[Any] = None,
    analyst_agent: Optional[Any] = None,
):
    """Conveniencia: arma y compila el grafo (sin checkpointer - esta fase
    no pide persistencia entre sesiones, a diferencia de la Fase 5)."""
    return build_graph(
        supervisor_model, research_model, analyst_model, research_agent, analyst_agent
    ).compile()
