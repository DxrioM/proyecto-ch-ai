"""Configuracion del Sistema Final: todo lo que depende del entorno sale de
variables de entorno (sin IDs de indices, namespaces ni modelos fijos en el
codigo). Los valores por defecto son los del proyecto y solo se usan si la
variable no esta definida.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / "data"


def get_setting(nombre: str, default: str | None = None) -> str | None:
    """Lee una variable de entorno cargando antes el .env de la raiz."""
    load_dotenv()
    return os.environ.get(nombre, default)


def get_required(nombre: str) -> str:
    """Igual que get_setting, pero falla con un mensaje claro si falta."""
    valor = get_setting(nombre)
    if not valor:
        raise ValueError(f"Falta {nombre} en .env")
    return valor


# Pinecone: el indice y el namespace ya existen con el corpus de la Fase 4,
# por eso el default es el de esa fase (evita reindexar a ciegas).
PINECONE_INDEX_NAME = get_setting("PINECONE_INDEX_NAME", "proyecto-ch-ai-fase4")
PINECONE_NAMESPACE = get_setting("PINECONE_NAMESPACE", "fase4-corpus")
PINECONE_TOP_K = int(get_setting("PINECONE_TOP_K", "5"))

# Modelo de razonamiento (Groq). Se cambia desde .env sin tocar codigo.
GROQ_MODEL = get_setting("GROQ_MODEL", "openai/gpt-oss-120b")

# Control de concurrencia y limites del grafo.
MAX_JOBS_CONCURRENTES = int(get_setting("MAX_JOBS_CONCURRENTES", "2"))
RECURSION_LIMIT = int(get_setting("RECURSION_LIMIT", "15"))

# Observabilidad.
LANGSMITH_PROJECT = get_setting("LANGSMITH_PROJECT", "proyecto-ch-ai-final")
