"""Fase 7: capa de observabilidad (LangSmith).

LangChain/LangGraph instrumentan sus propias llamadas a LLM automaticamente
en cuanto estas variables de entorno estan seteadas - no hace falta envolver
cada llamada a mano. init_observability() se llama una vez al arrancar la
API (ver main.py), antes de que se arme ningun grafo.
"""

import logging
import os

from dotenv import load_dotenv
from langsmith import traceable

logger = logging.getLogger("fase7_observability")

DEFAULT_PROJECT = "proyecto-ch-ai-fase7"


def init_observability() -> bool:
    """Activa el tracing de LangSmith si hay API key configurada.

    Devuelve True si la observabilidad quedo activa, False si se omitio
    (sin API key) - la API sigue funcionando igual sin observabilidad, solo
    sin trazas.
    """
    load_dotenv()
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        logger.warning("Falta LANGSMITH_API_KEY: la API va a correr SIN trazas de observabilidad.")
        return False

    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", DEFAULT_PROJECT)
    # Compatibilidad: algunas versiones de langchain-core todavia leen el
    # nombre de variable viejo (LANGCHAIN_*) en vez del nuevo (LANGSMITH_*).
    os.environ.setdefault("LANGCHAIN_TRACING_V2", os.environ["LANGSMITH_TRACING"])
    os.environ.setdefault("LANGCHAIN_API_KEY", api_key)
    os.environ.setdefault("LANGCHAIN_PROJECT", os.environ["LANGSMITH_PROJECT"])

    logger.info("Observabilidad activa: proyecto LangSmith '%s'", os.environ["LANGSMITH_PROJECT"])
    return True


# Decorador reutilizable para agrupar, en una sola traza nombrada, todo lo
# que pasa dentro de la ejecucion de un job (el grafo entero: supervisor +
# especialistas), en vez de ver cada llamada a LLM suelta sin contexto de a
# que job pertenece.
def traced_job(func):
    return traceable(name="ejecutar_job", run_type="chain")(func)
