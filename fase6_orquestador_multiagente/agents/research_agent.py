"""Agente de Busqueda/Investigacion.

Herramienta: busqueda simulada sobre la Vector DB de pre-entregas
anteriores (la consigna permite explicitamente Tavily O esto). Se reutiliza
el mismo ChromaDB local + corpus del "Sistema de Pedidos Online" indexado
en la Fase 3 (fase3_rag_local), en vez de depender de una API de busqueda
externa nueva.
"""

import asyncio
from pathlib import Path
from typing import Any, Optional

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from fase3_ejercicio_chromadb.vector_memory_manager import VectorMemoryManager

VECTORSTORE_DIR = Path(__file__).parent.parent.parent / "fase3_rag_local" / "vectorstore"
COLLECTION_NAME = "fase3_rag_local"

RESEARCH_SYSTEM_PROMPT = (
    "Sos el especialista de Investigacion de un sistema multi-agente. Tu "
    "unico trabajo es buscar informacion relevante en la base de "
    "conocimiento usando la herramienta buscar_en_base_de_conocimiento y "
    "resumir lo que encontraste, citando la fuente. Nunca inventes datos "
    "que no esten en los resultados de la herramienta. IMPORTANTE: "
    "reporta los valores numericos EXACTAMENTE como aparecen en la fuente "
    "(ej. '30 minutos', '4 horas habiles', '2 dias habiles'), sin "
    "convertirlos a otra unidad ni agregar una columna de equivalencias vos "
    "mismo. No hagas ningun calculo ni conversion de unidades: eso es "
    "trabajo exclusivo del especialista de Analisis despues."
)

_manager: Optional[VectorMemoryManager] = None


def _get_manager() -> VectorMemoryManager:
    global _manager
    if _manager is None:
        _manager = VectorMemoryManager(persist_path=str(VECTORSTORE_DIR), collection_name=COLLECTION_NAME)
    return _manager


@tool
async def buscar_en_base_de_conocimiento(query: str) -> dict:
    """Busca informacion relevante en la base de conocimiento vectorial del
    Sistema de Pedidos Online (arquitectura, despliegue, troubleshooting,
    politicas de soporte - el mismo corpus indexado en la Fase 3).

    Usa esta herramienta para investigar hechos, politicas o datos
    tecnicos documentados ANTES de que el especialista de Analisis procese
    esa informacion. Recibe una consulta en lenguaje natural y devuelve los
    3 fragmentos de texto mas relevantes, cada uno con su archivo fuente.
    Si la base esta vacia (primera vez que se corre), la indexa
    automaticamente antes de buscar.
    """
    manager = _get_manager()
    if manager.count() == 0:
        from fase3_rag_local.ingest import ingest

        await ingest()

    resultados = manager.semantic_search(query, n_results=3)
    return {
        "resultados": [
            {"fuente": r["metadata"].get("source", r["id"]), "texto": r["document"]} for r in resultados
        ]
    }


def build_research_agent(model: Any):
    """Arma el sub-agente de investigacion con create_react_agent: un mini
    ciclo ReAct propio (puede llamar la herramienta mas de una vez si hace
    falta) acotado a una sola herramienta."""
    return create_react_agent(model, tools=[buscar_en_base_de_conocimiento], prompt=RESEARCH_SYSTEM_PROMPT)


if __name__ == "__main__":

    async def _demo() -> None:
        resultado = await buscar_en_base_de_conocimiento.ainvoke(
            {"query": "tiempos de respuesta de soporte por severidad"}
        )
        for r in resultado["resultados"]:
            print(f"[{r['fuente']}] {r['texto'][:120]}...")

    asyncio.run(_demo())
