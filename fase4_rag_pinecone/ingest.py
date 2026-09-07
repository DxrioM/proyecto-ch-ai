"""Componente D - Fase 4: pipeline de ingesta hacia Pinecone Serverless.

Reutiliza deliberadamente piezas de fases/componentes anteriores en vez de
reimplementarlas: el chunking de la Fase 3 (DocumentProcessor), el corpus
de ejemplo de fase3_rag_local/data (el MISMO sistema, ahora escalado a la
nube), ensure_index_exists del Componente A, y el IngestionPipeline del
Componente B (batching + metadatos), con IDs deterministicos en vez de
uuid4 al azar para poder ser idempotente.
"""

import asyncio
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pinecone import Pinecone

from fase3_ejercicio_chunking.document_processor import DocumentProcessor
from fase4_ejercicio_ingesta_masiva.ingestion_pipeline import IngestionPipeline
from fase4_ejercicio_pinecone_setup.setup_infra import DEFAULT_DIMENSION, ensure_index_exists
from fase4_rag_pinecone.embeddings import LocalChromaEmbeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("fase4_ingest")

BASE_DIR = Path(__file__).parent
# Reutiliza el corpus de ejemplo de la Fase 3 (Sistema de Pedidos Online,
# ficticio) para demostrar que es el MISMO sistema RAG escalado a la nube,
# no uno nuevo. Ver fase4_rag_pinecone/data/README.md.
DATA_DIR = BASE_DIR.parent / "fase3_rag_local" / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
MANIFEST_PATH = VECTORSTORE_DIR / "manifest.json"
CHUNKS_CACHE_PATH = VECTORSTORE_DIR / "chunks_cache.json"

INDEX_NAME = "proyecto-ch-ai-fase4"
NAMESPACE = "fase4-corpus"


def _file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _save_json(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class PineconeAsyncAdapter:
    """Envuelve el indice sincronico real de Pinecone (pinecone-client es
    sync) con la misma interfaz async que MockPineconeIndex (Componente B),
    para poder reutilizar IngestionPipeline sin cambios contra un indice
    real, corriendo las llamadas bloqueantes en un thread aparte."""

    def __init__(self, index, namespace: str):
        self._index = index
        self._namespace = namespace

    async def upsert(self, vectors: List[dict]) -> dict:
        result = await asyncio.to_thread(self._index.upsert, vectors=vectors, namespace=self._namespace)
        return {"upserted_count": result.upserted_count}

    async def delete(self, ids: List[str]) -> None:
        if not ids:
            return
        await asyncio.to_thread(self._index.delete, ids=ids, namespace=self._namespace)


async def ingest(
    data_dir: Path = DATA_DIR,
    force: bool = False,
    manifest_path: Path = MANIFEST_PATH,
    chunks_cache_path: Path = CHUNKS_CACHE_PATH,
    pipeline: Optional[IngestionPipeline] = None,
    embeddings: Optional[LocalChromaEmbeddings] = None,
    processor: Optional[DocumentProcessor] = None,
) -> List[Dict[str, Any]]:
    """Fragmenta, embede y persiste el corpus en Pinecone de forma
    idempotente (mismo criterio que fase3_rag_local/ingest.py: hash por
    archivo + limpieza de chunks huerfanos si un archivo se achica).

    pipeline/embeddings/processor son inyectables para poder testear la
    logica de idempotencia y limpieza de chunks huerfanos con dobles
    falsos, sin depender de Pinecone/el modelo de embeddings reales (ver
    tests/). Si no se pasa pipeline, se arma uno real contra Pinecone.

    Devuelve la lista de chunks indexados ({"id","text","metadata"}), para
    que rag_system.py arme el retriever BM25 local sin tener que releer ni
    refragmentar los archivos fuente.
    """
    if pipeline is None:
        load_dotenv()
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("Falta PINECONE_API_KEY en .env")

        pc = Pinecone(api_key=api_key)
        await ensure_index_exists(pc, INDEX_NAME, DEFAULT_DIMENSION)
        index = pc.Index(INDEX_NAME)
        adapter = PineconeAsyncAdapter(index, namespace=NAMESPACE)
        # text_snippet_length=None: la consigna de esta fase pide guardar
        # el TEXTO ORIGINAL COMPLETO en la metadata (a diferencia del
        # snippet corto del enunciado generico del Componente B).
        pipeline = IngestionPipeline(adapter, text_snippet_length=None)

    embeddings = embeddings or LocalChromaEmbeddings()
    # 600 tokens, dentro del rango 500-800 recomendado por la consigna de
    # esta fase (ni muy chico -> pierde contexto, ni muy grande -> diluye
    # la precision del embedding).
    processor = processor or DocumentProcessor(chunk_size=600, chunk_overlap=100)

    manifest = {} if force else _load_json(manifest_path, {})
    cache_previo = [] if force else _load_json(chunks_cache_path, [])
    chunks_por_archivo: Dict[str, List[dict]] = {}
    for c in cache_previo:
        chunks_por_archivo.setdefault(c["metadata"]["source"], []).append(c)

    new_manifest: Dict[str, dict] = {}

    source_files = sorted(data_dir.glob("*.md")) + sorted(data_dir.glob("*.txt"))
    if not source_files:
        raise ValueError(f"No se encontraron archivos .md/.txt en {data_dir}")

    for path in source_files:
        text = path.read_text(encoding="utf-8")
        current_hash = _file_hash(text)
        previous = manifest.get(path.name)

        if previous and previous.get("hash") == current_hash:
            logger.info("Sin cambios, se omite la reingesta: %s", path.name)
            new_manifest[path.name] = previous
            continue

        chunks = processor.process_document(text)
        ids = [f"{path.stem}_{i}" for i in range(len(chunks))]
        vectores = embeddings.embed_documents(chunks)

        documentos = [
            {
                "id_deterministico": ids[i],
                "text": chunks[i],
                "embedding": vectores[i],
                "category": path.stem,
                "author": "sistema-pedidos-online",
            }
            for i in range(len(chunks))
        ]

        # Si la version anterior de este archivo genero mas chunks que la
        # nueva, borra los IDs que sobran para no dejar contenido
        # desactualizado huerfano en el indice.
        previous_chunk_count = previous.get("chunk_count", 0) if previous else 0
        if previous_chunk_count > len(chunks):
            stale_ids = [f"{path.stem}_{i}" for i in range(len(chunks), previous_chunk_count)]
            # pipeline.index es el adapter (real o falso) que se le paso a
            # IngestionPipeline; reutilizarlo aca evita mantener una
            # referencia aparte al adapter real.
            await pipeline.index.delete(stale_ids)
            logger.info("Borrados %d chunks huerfanos de %s", len(stale_ids), path.name)

        await pipeline.process_and_upsert_batches(
            documentos, id_generator=lambda _i, doc: doc["id_deterministico"]
        )
        logger.info("Indexado en Pinecone: %s (%d chunks)", path.name, len(chunks))

        chunks_por_archivo[path.name] = [
            {
                "id": ids[i],
                "text": chunks[i],
                "metadata": {"source": path.name, "chunk_index": i, "category": path.stem},
            }
            for i in range(len(chunks))
        ]
        new_manifest[path.name] = {"hash": current_hash, "chunk_count": len(chunks)}

    todos_los_chunks = [c for archivo_chunks in chunks_por_archivo.values() for c in archivo_chunks]

    _save_json(new_manifest, manifest_path)
    _save_json(todos_los_chunks, chunks_cache_path)
    logger.info("Ingesta completa. %d chunks en total (namespace='%s').", len(todos_los_chunks), NAMESPACE)
    return todos_los_chunks


if __name__ == "__main__":
    asyncio.run(ingest())
