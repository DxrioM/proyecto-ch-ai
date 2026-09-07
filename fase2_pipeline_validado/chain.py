"""Cadena LCEL del Pipeline de Extraccion de Entidades Tecnicas.

prompt | model.with_structured_output(TechExtraction), con reintentos
automaticos (.with_retry()) ante JSON mal formado o incompleto.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

from .schemas import TechExtraction

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("fase2_pipeline_validado")

SYSTEM_PROMPT = (
    "Sos un analista tecnico. A partir de un parrafo de descripcion de "
    "arquitectura de software o de un log de error, extrae: las tecnologias "
    "mencionadas, el nivel de criticidad tecnica (baja, media o alta) y un "
    "resumen tecnico breve. Si el texto no menciona ninguna tecnologia de "
    "forma explicita, inferi la tecnologia mas probable a partir del "
    "contexto en vez de dejar la lista vacia."
)


def build_chain(resilient_model: Optional[Runnable] = None):
    """Compone prompt | model.with_structured_output(TechExtraction) + retry.

    resilient_model es inyectable para poder testear la cadena con un
    Runnable falso (ver tests/), sin depender de la API real de Groq. Si no
    se pasa, se arma el modelo real con ChatGroq.
    """
    if resilient_model is None:
        load_dotenv()
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Falta GROQ_API_KEY en .env")

        model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key)
        structured_model = model.with_structured_output(TechExtraction)

        # Resiliencia: reintenta ante fallos transitorios (red, rate limit) o
        # ante una respuesta del LLM que no valida contra el esquema Pydantic.
        resilient_model = structured_model.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True,
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{texto}"),
        ]
    )

    return prompt | resilient_model


async def process_text(text: str, resilient_model: Optional[Runnable] = None) -> Optional[TechExtraction]:
    """Procesa un parrafo de texto y devuelve un TechExtraction validado.

    Nunca deja escapar una excepcion: si falla la validacion o la conexion
    incluso despues de los reintentos, devuelve None y deja el error en los
    logs, para que el llamador decida como continuar (fallback, alerta, etc.).
    """
    chain = build_chain(resilient_model)
    logger.info("Procesando texto (%d caracteres)", len(text))
    try:
        resultado = await chain.ainvoke({"texto": text})
        logger.info("Extraccion validada OK: criticidad=%s", resultado.nivel_de_criticidad)
        return resultado
    except Exception as e:
        # Incluye ValidationError de Pydantic (JSON con tipos/valores
        # incorrectos) y errores de red/rate limit que sobrevivieron los
        # reintentos de with_retry().
        logger.error("Fallo la extraccion (%s): %s", type(e).__name__, e)
        return None
