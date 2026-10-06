"""Composicion del grafo del Sistema Final: supervisor + especialistas, con
checkpointer de Redis (persistencia entre reinicios) y el gate HITL antes
del analista.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt
from redis.asyncio import Redis

from sistema_final.config import get_required
from sistema_final.hitl import construir_payload_aprobacion
from sistema_final.redis_checkpointer import RedisCheckpointSaver
from sistema_final.state import OrchestratorState
from sistema_final.supervisor import build_graph


def _hitl_gate(state: OrchestratorState) -> None:
    """Pausa el grafo (interrupt) al principio del nodo analista hasta que
    llegue una aprobacion via POST /tasks/{id}/approve. El checkpointer de
    Redis guarda el estado pausado, asi que la API puede reiniciarse mientras
    un job espera aprobacion."""
    pregunta_original = state["messages"][0].content if state["messages"] else ""
    hallazgos = "\n".join(
        c["resumen"] for c in state.get("contribuciones", []) if c["agente"] == "investigador"
    )
    interrupt(construir_payload_aprobacion(pregunta_original, hallazgos))


@asynccontextmanager
async def redis_checkpointer(redis_url: Optional[str] = None) -> AsyncIterator[RedisCheckpointSaver]:
    """Abre el checkpointer de Redis como recurso de vida larga. Usa el
    RedisCheckpointSaver propio porque langgraph-checkpoint-redis necesita
    RediSearch (FT.*), que Upstash no soporta."""
    cliente = Redis.from_url(redis_url or get_required("REDIS_URL"), decode_responses=True)
    try:
        yield RedisCheckpointSaver(cliente)
    finally:
        await cliente.aclose()


def compile_graph(
    checkpointer: Any,
    supervisor_model: Optional[Any] = None,
    research_agent: Optional[Any] = None,
    analyst_agent: Optional[Any] = None,
) -> CompiledStateGraph:
    """Arma y compila el grafo con el checkpointer dado y el gate HITL. Los
    modelos y agentes son inyectables para testear sin Groq ni Redis reales."""
    graph = build_graph(
        supervisor_model=supervisor_model,
        research_agent=research_agent,
        analyst_agent=analyst_agent,
        hitl_gate=_hitl_gate,
    )
    return graph.compile(checkpointer=checkpointer)
