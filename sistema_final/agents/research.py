"""Agente de Investigacion.

Herramienta: busqueda hibrida (Pinecone + BM25) sobre el corpus del Sistema
de Pedidos Online. La entrada se valida con Pydantic antes de buscar, y la
busqueda es asincrona (no bloquea el event loop).
"""

from typing import Any

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from sistema_final.rag.hybrid import get_rag

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


class BuscarEnBaseInput(BaseModel):
    """Entrada validada de buscar_en_base_de_conocimiento."""

    query: str = Field(min_length=3, max_length=500, description="Consulta en lenguaje natural")


@tool(args_schema=BuscarEnBaseInput)
async def buscar_en_base_de_conocimiento(query: str) -> dict:
    """Busca informacion relevante en la base de conocimiento del Sistema de
    Pedidos Online (arquitectura, despliegue, troubleshooting, politicas de
    soporte). Usala para investigar hechos, politicas o datos tecnicos
    documentados ANTES de que el especialista de Analisis procese esa
    informacion. Devuelve los fragmentos mas relevantes, cada uno con su
    archivo fuente.
    """
    documentos = await get_rag().aretrieve(query)
    return {
        "resultados": [
            {"fuente": d.metadata.get("source", d.metadata.get("id")), "texto": d.page_content} for d in documentos
        ]
    }


def build_research_agent(model: Any):
    """Arma el sub-agente de investigacion con create_react_agent, acotado a
    una sola herramienta."""
    return create_react_agent(model, tools=[buscar_en_base_de_conocimiento], prompt=RESEARCH_SYSTEM_PROMPT)
