"""Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.

Resuelve el ejercicio de la catedra (con_structured_output + with_retry),
adaptado de ChatOpenAI a ChatGroq (proveedor gratuito, ver seccion 5/6 del
contexto de la Fase 2).
"""

import asyncio
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


class EntityExtraction(BaseModel):
    """Contrato de datos validado que debe devolver el LLM."""

    topic: str = Field(description="Tema principal del texto")
    entities: List[str] = Field(description="Entidades mencionadas en el texto")
    sentiment_score: float = Field(ge=0, le=1, description="Puntaje de sentimiento, 0 a 1")
    complexity_level: Optional[str] = Field(
        default=None,
        pattern="^(Low|Medium|High)$",
        description="Nivel de complejidad del texto, si se puede inferir",
    )


async def run_validated_chain(text: str) -> Optional[EntityExtraction]:
    """Extrae entidades del texto de forma validada y resiliente ante fallos."""
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Falta GROQ_API_KEY en .env")

    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key)

    # Salida estructurada: el LLM debe devolver un EntityExtraction valido,
    # no texto libre que despues haya que parsear a mano.
    structured_llm = llm.with_structured_output(EntityExtraction)

    # Resiliencia: reintenta hasta 3 veces ante fallos transitorios de red,
    # rate limit o JSON mal formado, con backoff exponencial con jitter.
    resilient_llm = structured_llm.with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Analiza el texto y extrae las entidades."),
            ("human", "{input}"),
        ]
    )

    chain = prompt | resilient_llm

    try:
        result = await chain.ainvoke({"input": text})
        print("Extraccion validada exitosa:")
        print(result.model_dump_json(indent=2))
        return result
    except Exception as e:
        # Nunca dejar escapar la excepcion: puede ser un error de red
        # despues de agotar los reintentos, o un ValidationError de Pydantic
        # si el LLM devolvio JSON valido pero con tipos/valores incorrectos.
        print(f"Error ({type(e).__name__}): {e}")
        return None


if __name__ == "__main__":
    sample_text = "LangGraph es una extension de LangChain para agentes ciclicos."
    asyncio.run(run_validated_chain(sample_text))
