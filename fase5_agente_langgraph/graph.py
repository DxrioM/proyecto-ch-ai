"""Fase 5: definicion del grafo de razonamiento (StateGraph de LangGraph).

Nodo de modelo (LLM con herramientas vinculadas via bind_tools) + nodo de
ejecucion de herramientas (ToolNode) + arista condicional (tools_condition):
el LLM decide por si mismo, en base al prompt del usuario, si necesita
llamar a una herramienta o si ya puede responder directamente - sin rutas
if/else manuales. Esa es la autonomia que pide la consigna.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import buscar_pedidos, obtener_detalle_pedido

TOOLS = [buscar_pedidos, obtener_detalle_pedido]

SYSTEM_PROMPT = (
    "Sos un asistente del Sistema de Pedidos Online. Respondes preguntas "
    "sobre pedidos de clientes usando las herramientas disponibles. Nunca "
    "inventes datos de pedidos: siempre consulta la herramienta "
    "correspondiente antes de responder. Si una herramienta devuelve un "
    "error (por ejemplo, un cliente o pedido que no existe), explicaselo "
    "al usuario con claridad en vez de inventar una respuesta, y pedile "
    "que confirme el dato si parece un error de tipeo."
)


def _build_model():
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Falta GROQ_API_KEY en .env")
    model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key)
    return model.bind_tools(TOOLS)


def build_graph(model: Optional[Any] = None) -> StateGraph:
    """Arma el grafo (sin compilar: el caller decide el checkpointer).

    model es inyectable (ya debe venir con .bind_tools(TOOLS) aplicado) para
    poder testear la logica de ruteo del grafo con un LLM falso, sin
    depender de la API real de Groq.
    """
    llm_with_tools = model or _build_model()

    async def call_model(state: MessagesState) -> dict:
        mensajes = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
        respuesta = await llm_with_tools.ainvoke(mensajes)
        return {"messages": [respuesta]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    # Arista condicional: tools_condition mira el ultimo mensaje del LLM y
    # rutea a "tools" si tiene tool_calls, o termina (END) si ya puede
    # responder. Ningun if/else manual decide esto.
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph


def compile_graph(checkpointer, model: Optional[Any] = None) -> CompiledStateGraph:
    """Conveniencia: arma y compila el grafo con el checkpointer dado."""
    return build_graph(model).compile(checkpointer=checkpointer)
