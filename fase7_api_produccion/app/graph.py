"""Fase 7: el orquestador multi-agente de la Fase 6 + persistencia en Redis
+ un punto de interrupcion Human-in-the-loop antes de que el Analista
ejecute.

Reutiliza fase6_orquestador_multiagente.graph.build_graph() tal cual (no
duplica el Supervisor ni los especialistas), inyectando el gate HITL via el
parametro hitl_gate agregado especificamente para esta fase.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from dotenv import load_dotenv

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt
from redis.asyncio import Redis

from fase6_orquestador_multiagente.graph import build_graph as build_orchestrator_graph
from fase6_orquestador_multiagente.state import OrchestratorState

from .hitl import construir_payload_aprobacion
from .redis_checkpointer import RedisCheckpointSaver


def _hitl_gate(state: OrchestratorState) -> None:
    """Se ejecuta al principio del nodo 'analista'. Pausa el grafo
    (interrupt) hasta que llegue una aprobacion externa via
    POST /tasks/{id}/approve. Reutiliza interrupt() de LangGraph: el
    checkpointer (Redis) persiste el estado pausado, asi que el proceso de
    la API puede incluso reiniciarse mientras un job espera aprobacion."""
    pregunta_original = state["messages"][0].content if state["messages"] else ""
    hallazgos = "\n".join(
        c["resumen"] for c in state.get("contribuciones", []) if c["agente"] == "investigador"
    )
    interrupt(construir_payload_aprobacion(pregunta_original, hallazgos))


@asynccontextmanager
async def redis_checkpointer(redis_url: Optional[str] = None) -> AsyncIterator[RedisCheckpointSaver]:
    """Abre un checkpointer de Redis como recurso de vida larga (una vez al
    arrancar la API, ver main.py's lifespan). Usa RedisCheckpointSaver
    propio en vez de langgraph-checkpoint-redis, porque este necesita
    RediSearch (FT.*), que Upstash no soporta."""
    load_dotenv()
    redis_url = redis_url or os.environ.get("REDIS_URL")
    if not redis_url:
        raise ValueError("Falta REDIS_URL en .env")
    cliente = Redis.from_url(redis_url, decode_responses=True)
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
    """Arma y compila el grafo con el checkpointer dado y el gate HITL.

    Los modelos/agentes son inyectables (mismo criterio que la Fase 6) para
    poder testear el flujo completo (incluida la pausa HITL) sin depender
    de la API real de Groq ni de Redis real."""
    graph = build_orchestrator_graph(
        supervisor_model=supervisor_model,
        research_agent=research_agent,
        analyst_agent=analyst_agent,
        hitl_gate=_hitl_gate,
    )
    return graph.compile(checkpointer=checkpointer)
