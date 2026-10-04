"""Fase 5: script de demo - razonamiento ciclico con memoria persistente.

Corre tres interacciones sobre el MISMO thread_id (memoria compartida via
checkpointer SQLite):

1. Pregunta inicial que requiere llamar a buscar_pedidos (1 herramienta).
2. Pregunta de seguimiento ("el ultimo pedido?") que requiere RECORDAR el
   contexto del turno anterior Y llamar a una segunda herramienta distinta
   (obtener_detalle_pedido) - razonamiento multi-paso real, sin repetir el
   cliente_id en el prompt.
3. Pregunta sobre un cliente inexistente, para demostrar el ciclo de
   retorno: la herramienta devuelve un error y el agente lo explica en vez
   de inventar una respuesta o romperse.

Guarda la traza completa del thread (todos los mensajes, incluidas las
tool calls y sus resultados) en traces/ejemplo_traza.json.
"""

import asyncio
import json
import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .graph import compile_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("fase5_agente")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "checkpoints.sqlite"
TRACE_PATH = BASE_DIR / "traces" / "ejemplo_traza.json"

# Techo de pasos del grafo por invocacion: evita bucles infinitos y costos
# inesperados de API si el agente quedara reintentando sin converger.
RECURSION_LIMIT = 10


def _message_to_dict(message) -> dict:
    """Serializa un mensaje de LangChain a un dict legible, para el log/JSON
    de la traza (no se usa el .dict() crudo de LangChain: tiene mucho ruido
    interno que no aporta a la evidencia de razonamiento)."""
    base = {"tipo": message.__class__.__name__, "contenido": message.content}
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        base["tool_calls"] = [{"herramienta": tc["name"], "argumentos": tc["args"]} for tc in tool_calls]
    if isinstance(message, ToolMessage):
        base["herramienta"] = message.name
    return base


async def preguntar(app, pregunta: str, config: dict) -> str:
    logger.info("Usuario: %s", pregunta)
    resultado = await app.ainvoke({"messages": [HumanMessage(content=pregunta)]}, config=config)
    respuesta = resultado["messages"][-1].content
    logger.info("Agente: %s", respuesta)
    return respuesta


async def main() -> None:
    async with AsyncSqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        app = compile_graph(checkpointer)
        thread_id = "demo-cliente-102"
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}

        print("=== Turno 1: pregunta inicial (1 llamada a herramienta) ===")
        await preguntar(app, "Cuantos pedidos tuvo el cliente 102 y cual fue el total?", config)

        print("\n=== Turno 2: seguimiento con memoria (recordar + 2da herramienta) ===")
        await preguntar(app, "Y cual es el detalle del ultimo pedido?", config)

        print("\n=== Turno 3: cliente inexistente (ciclo de retorno ante error) ===")
        await preguntar(app, "Cuantos pedidos tuvo el cliente 999?", config)

        # Trae el historial completo persistido para este thread_id (todo
        # lo que recuerda el checkpointer) y lo guarda como traza.
        estado_final = await app.aget_state(config)
        traza = [_message_to_dict(m) for m in estado_final.values["messages"]]

        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TRACE_PATH.write_text(json.dumps(traza, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Traza guardada en %s (%d mensajes)", TRACE_PATH, len(traza))


if __name__ == "__main__":
    asyncio.run(main())
