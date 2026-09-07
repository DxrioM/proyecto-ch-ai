"""Componente D - Fase 3: modulo de ingesta (chunking + persistencia en ChromaDB).

Lee los archivos .md/.txt de ./data, los fragmenta con el DocumentProcessor
del Componente B y los persiste con el VectorMemoryManager del Componente C.
Idempotente: si un archivo no cambio desde la ultima corrida (mismo hash de
contenido), no se vuelve a fragmentar ni a re-embeder.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from fase3_ejercicio_chromadb.vector_memory_manager import VectorMemoryManager
from fase3_ejercicio_chunking.document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("ingest")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
COLLECTION_NAME = "fase3_rag_local"
MANIFEST_PATH = VECTORSTORE_DIR / "manifest.json"


def _file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_manifest(manifest_path: Path) -> Dict[str, dict]:
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def _save_manifest(manifest: Dict[str, dict], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def ingest(
    data_dir: Path = DATA_DIR,
    force: bool = False,
    manager: Optional[VectorMemoryManager] = None,
    processor: Optional[DocumentProcessor] = None,
    manifest_path: Path = MANIFEST_PATH,
) -> VectorMemoryManager:
    """Fragmenta y persiste los archivos de data_dir en ChromaDB de forma
    idempotente. Si force=True, ignora el manifest y reindexa todo.

    manager y processor son inyectables para poder testear la logica de
    idempotencia y limpieza de chunks huerfanos con dobles falsos, sin
    depender de ChromaDB/tiktoken reales (ver tests/).
    """
    manager = manager or VectorMemoryManager(persist_path=str(VECTORSTORE_DIR), collection_name=COLLECTION_NAME)
    processor = processor or DocumentProcessor()
    manifest = {} if force else _load_manifest(manifest_path)
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
        metadatas = [{"source": path.name, "chunk_index": i} for i in range(len(chunks))]

        # Si la version anterior de este archivo genero mas chunks que la
        # nueva, hay que borrar los IDs que sobran para no dejar chunks
        # huerfanos con contenido viejo en la coleccion.
        previous_chunk_count = previous.get("chunk_count", 0) if previous else 0
        if previous_chunk_count > len(chunks):
            stale_ids = [f"{path.stem}_{i}" for i in range(len(chunks), previous_chunk_count)]
            manager.delete_by_id(stale_ids)

        manager.upsert_documents(ids, chunks, metadatas)
        logger.info("Indexado: %s (%d chunks)", path.name, len(chunks))
        new_manifest[path.name] = {"hash": current_hash, "chunk_count": len(chunks)}

    _save_manifest(new_manifest, manifest_path)
    logger.info("Ingesta completa. Documentos en la coleccion: %d", manager.count())
    return manager


if __name__ == "__main__":
    ingest()
