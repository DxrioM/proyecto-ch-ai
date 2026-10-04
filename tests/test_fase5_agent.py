"""Tests sinteticos para la Fase 5 (agente ReAct con LangGraph).

1. Herramientas: deterministas, sin LLM (casos de exito y de error).
2. Ruteo del grafo (tools_condition): con un LLM falso, para probar que el
   grafo ejecuta la herramienta real cuando el modelo decide llamarla y
   corta el ciclo cuando ya puede responder - sin depender de la API real
   de Groq ni de que el LLM "decida" lo mismo en cada corrida.
"""

import asyncio

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from fase5_agente_langgraph.graph import compile_graph
from fase5_agente_langgraph.tools import buscar_pedidos, obtener_detalle_pedido

# ---------------------------------------------------------------------------
# 1. Herramientas
# ---------------------------------------------------------------------------


def test_buscar_pedidos_cliente_existente():
    resultado = buscar_pedidos.invoke({"cliente_id": 102})

    assert resultado["pedidos"] == 3
    assert resultado["total"] == 14500.0
    assert resultado["pedido_ids"] == [5001, 5002, 5003]


def test_buscar_pedidos_cliente_inexistente_devuelve_error_sin_crashear():
    resultado = buscar_pedidos.invoke({"cliente_id": 999})

    assert "error" in resultado
    assert "999" in resultado["error"]


def test_obtener_detalle_pedido_existente():
    resultado = obtener_detalle_pedido.invoke({"pedido_id": 5003})

    assert resultado["estado"] == "en camino"
    assert resultado["productos"] == ["Silla ergonomica"]


def test_obtener_detalle_pedido_inexistente_devuelve_error_sin_crashear():
    resultado = obtener_detalle_pedido.invoke({"pedido_id": 99999})

    assert "error" in resultado


# ---------------------------------------------------------------------------
# 2. Ruteo del grafo (tools_condition) con un LLM falso
# ---------------------------------------------------------------------------


class _FakeModelOneToolCall:
    """Decide llamar a buscar_pedidos en el primer turno y responde directo
    en el segundo (sin tool_calls) - simula el patron ReAct de un paso."""

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[{"name": "buscar_pedidos", "args": {"cliente_id": 102}, "id": "call_1"}],
            )
        return AIMessage(content="El cliente 102 tiene 3 pedidos.")


class _FakeModelNoToolNeeded:
    """Nunca llama a ninguna herramienta: el grafo debe terminar despues de
    un solo paso (tools_condition corta el ciclo, no fuerza una llamada)."""

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        return AIMessage(content="Hola! En que puedo ayudarte?")


def test_graph_calls_tool_when_model_decides_to():
    fake_model = _FakeModelOneToolCall()
    app = compile_graph(MemorySaver(), model=fake_model)
    config = {"configurable": {"thread_id": "test-1"}, "recursion_limit": 10}

    resultado = asyncio.run(
        app.ainvoke({"messages": [HumanMessage(content="cuantos pedidos tiene el cliente 102?")]}, config=config)
    )

    assert fake_model.calls == 2  # 1 decide llamar la herramienta, 1 responde con el resultado
    assert "3 pedidos" in resultado["messages"][-1].content
    # La herramienta REAL se ejecuto (no un mock): el resultado real de
    # buscar_pedidos(102) debe estar en algun ToolMessage del historial.
    tool_messages = [m for m in resultado["messages"] if m.__class__.__name__ == "ToolMessage"]
    assert len(tool_messages) == 1
    assert "14500" in tool_messages[0].content


def test_graph_ends_without_tool_call_when_not_needed():
    fake_model = _FakeModelNoToolNeeded()
    app = compile_graph(MemorySaver(), model=fake_model)
    config = {"configurable": {"thread_id": "test-2"}, "recursion_limit": 10}

    resultado = asyncio.run(app.ainvoke({"messages": [HumanMessage(content="hola")]}, config=config))

    assert fake_model.calls == 1  # no hizo falta un segundo paso
    assert resultado["messages"][-1].content == "Hola! En que puedo ayudarte?"


def test_graph_remembers_across_turns_with_same_thread_id():
    """Prueba de persistencia: el mismo thread_id en dos invocaciones
    distintas debe acumular los mensajes de ambos turnos en el estado."""
    fake_model = _FakeModelNoToolNeeded()
    app = compile_graph(MemorySaver(), model=fake_model)
    config = {"configurable": {"thread_id": "test-memoria"}, "recursion_limit": 10}

    asyncio.run(app.ainvoke({"messages": [HumanMessage(content="primer turno")]}, config=config))
    resultado = asyncio.run(app.ainvoke({"messages": [HumanMessage(content="segundo turno")]}, config=config))

    textos_usuario = [
        m.content for m in resultado["messages"] if m.__class__.__name__ == "HumanMessage"
    ]
    assert textos_usuario == ["primer turno", "segundo turno"]
