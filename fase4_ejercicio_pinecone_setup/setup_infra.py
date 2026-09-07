"""Componente A - Fase 4: Pinecone Serverless, persistencia vectorial en la nube.

Automatiza la creacion de infraestructura Pinecone: crea el indice
Serverless solo si no existe (idempotente), espera a que este listo, y
hace un upsert de prueba en un namespace separado.

Requiere PINECONE_API_KEY en el .env de la raiz del proyecto.
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("setup_infra")

# 384 = dimension del modelo de embeddings local usado en el proyecto
# (Sentence Transformers all-MiniLM-L6-v2, el mismo que la Fase 3 y el
# Componente D de esta fase). No es obligatorio usar 1536: la dimension
# del indice debe coincidir con el modelo de embeddings elegido, no con un
# valor fijo.
DEFAULT_DIMENSION = 384


async def ensure_index_exists(pc: Pinecone, index_name: str, dimension: int = DEFAULT_DIMENSION) -> None:
    """Crea el indice Serverless si no existe (idempotente) y espera a que
    este listo. Reutilizable desde otros componentes (ver
    fase4_rag_pinecone/ingest.py) sin repetir el upsert de prueba."""
    if index_name not in pc.list_indexes().names():
        logger.info("El indice '%s' no existe, creandolo (dimension=%d)...", index_name, dimension)
        pc.create_index(
            name=index_name,
            dimension=dimension,
            # coseno: la metrica correcta para embeddings de Sentence
            # Transformers (entrenados y normalizados para similitud
            # coseno, no distancia euclidiana).
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            logger.info("Esperando a que el indice este listo...")
            await asyncio.sleep(1)
        logger.info("Indice '%s' creado y listo.", index_name)
    else:
        logger.info("El indice '%s' ya existe, se reutiliza (idempotente).", index_name)


async def setup_vector_infrastructure(index_name: str, dimension: int = DEFAULT_DIMENSION):
    """Configura la infraestructura de Pinecone Serverless y realiza una
    carga inicial de prueba."""
    load_dotenv()
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("Falta PINECONE_API_KEY en .env")

    pc = Pinecone(api_key=api_key)
    await ensure_index_exists(pc, index_name, dimension)
    index = pc.Index(index_name)

    # Upsert de prueba en un namespace separado ("dev-environment"), para
    # no mezclar datos de prueba con los datos reales de produccion que
    # use fase4_rag_pinecone.
    sample_vectors = [
        ("vec1", [0.1] * dimension, {"topic": "infraestructura", "priority": "high"}),
        ("vec2", [0.2] * dimension, {"topic": "seguridad", "priority": "medium"}),
    ]
    index.upsert(vectors=sample_vectors, namespace="dev-environment")
    logger.info("Upsert de prueba OK (namespace='dev-environment').")

    stats = index.describe_index_stats()
    logger.info("Estadisticas del indice: %s", stats)
    return index


if __name__ == "__main__":
    asyncio.run(setup_vector_infrastructure("proyecto-ch-ai-fase4", DEFAULT_DIMENSION))
