"""Componente D - Fase 3: capa de recuperacion + generacion grounded (RAG).

retriever (ChromaDB) -> prompt con el contexto recuperado -> LLM (Groq,
reutilizando el patron LCEL de la Fase 2) -> salida validada con Pydantic.
"""

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from fase3_ejercicio_chromadb.vector_memory_manager import VectorMemoryManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("rag_chain")

# Entre 3 y 5, nunca mas: evita el problema de "contexto infinito" /
# "Lost in the Middle" (el LLM pierde precision con demasiados fragmentos).
TOP_K = 4

SYSTEM_PROMPT = (
    "Sos un asistente tecnico. Respondes UNICAMENTE en base al CONTEXTO "
    "que se te proporciona abajo. Si la respuesta no esta en el contexto, "
    "decis explicitamente que no tenes esa informacion en la base de "
    "conocimiento; nunca inventes ni completes con conocimiento externo. "
    "Indica en 'fuentes' los nombres de archivo del contexto que "
    "efectivamente usaste para responder; si no usaste ninguno, dejalo "
    "vacio."
)


class RagResponse(BaseModel):
    """Salida validada de la cadena RAG."""

    respuesta: str = Field(description="Respuesta en espanol, basada solo en el contexto recuperado")
    fuentes: List[str] = Field(
        default_factory=list, description="Nombres de archivo de los chunks usados para responder"
    )
    encontrado_en_contexto: bool = Field(
        description="True si la respuesta esta respaldada por el contexto, False si no se encontro"
    )


def build_generation_chain(resilient_model: Optional[Runnable] = None):
    """Compone prompt | model.with_structured_output(RagResponse) + retry.

    resilient_model es inyectable para poder testear la cadena con un
    Runnable falso, igual que en fase2_pipeline_validado/chain.py.
    """
    if resilient_model is None:
        load_dotenv()
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Falta GROQ_API_KEY en .env")

        model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key)
        structured_model = model.with_structured_output(RagResponse)
        resilient_model = structured_model.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True,
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
        ]
    )

    return prompt | resilient_model


def format_context(resultados: List[dict]) -> str:
    """Convierte los resultados de semantic_search en un bloque de texto,
    citando la fuente de cada fragmento para que el modelo pueda referenciarla."""
    if not resultados:
        return "(no se encontro ningun fragmento relevante en la base vectorial)"
    partes = []
    for r in resultados:
        fuente = r["metadata"].get("source", r["id"])
        partes.append(f"[Fuente: {fuente}]\n{r['document']}")
    return "\n\n".join(partes)


async def get_rag_response(
    query: str,
    manager: VectorMemoryManager,
    chain: Optional[Runnable] = None,
    top_k: int = TOP_K,
) -> RagResponse:
    """Flujo RAG end-to-end asincrono: recupera contexto relevante en
    ChromaDB y genera una respuesta grounded (basada solo en ese contexto).

    Nunca deja escapar una excepcion: si la generacion falla incluso
    despues de los reintentos de with_retry() (error de red persistente) o
    el LLM devuelve algo que no valida contra RagResponse, se loggea el
    error y se devuelve una RagResponse de fallback en vez de romper el
    programa (mismo criterio que entregable_b_llm_client y
    fase2_pipeline_validado)."""
    chain = chain or build_generation_chain()

    resultados = manager.semantic_search(query, n_results=top_k)
    contexto = format_context(resultados)

    try:
        return await chain.ainvoke({"contexto": contexto, "pregunta": query})
    except Exception as e:
        logger.error("Fallo la generacion RAG (%s): %s", type(e).__name__, e)
        return RagResponse(
            respuesta="No se pudo generar una respuesta por un error tecnico. Intenta de nuevo mas tarde.",
            fuentes=[],
            encontrado_en_contexto=False,
        )
