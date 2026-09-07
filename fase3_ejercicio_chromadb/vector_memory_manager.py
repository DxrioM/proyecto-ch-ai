"""Componente C - Fase 3: Persistencia local con ChromaDB (operaciones CRUD).

Encapsula ChromaDB en una clase robusta: persistencia real en disco (nunca
cliente en memoria), IDs deterministicos, upsert (no add, para no romper en
reingestas), busqueda semantica y borrado.
"""

import logging
from typing import Any, Dict, List

import chromadb
from chromadb.errors import ChromaError
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("vector_memory_manager")


class VectorMemoryManager:
    """Encapsula una coleccion de ChromaDB persistida en disco."""

    def __init__(self, persist_path: str, collection_name: str):
        # PersistentClient con ruta en disco: sin esto se pierden los datos
        # al cerrar el script (el modo por defecto de Chroma es en memoria).
        self.client = chromadb.PersistentClient(path=persist_path)

        # Funcion de embedding local (Sentence Transformers via ONNX,
        # gratis, sin API key). Critico usar la MISMA funcion para indexar y
        # para consultar: es el error #1 de la catedra ("embeddings no
        # coincidentes"). get_or_create_collection la asocia una sola vez a
        # la coleccion; Chroma la reutiliza automaticamente en cada query.
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

    def upsert_documents(
        self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]
    ) -> bool:
        """Inserta o actualiza documentos. upsert (no add) para que una
        reingesta con los mismos IDs actualice en vez de fallar."""
        try:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            logger.info("Upsert OK: %d documento(s)", len(ids))
            return True
        except ChromaError as e:
            logger.error("Fallo el upsert en ChromaDB (%s): %s", type(e).__name__, e)
            return False

    def semantic_search(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Busqueda por similitud semantica. Devuelve los n_results documentos
        mas cercanos al query_text, con su distancia y metadata."""
        try:
            raw = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
        except ChromaError as e:
            logger.error("Fallo la busqueda semantica (%s): %s", type(e).__name__, e)
            return []

        ids = raw.get("ids", [[]])[0]
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        return [
            {"id": i, "document": d, "metadata": m, "distance": dist}
            for i, d, m, dist in zip(ids, documents, metadatas, distances)
        ]

    def delete_by_id(self, ids: List[str]) -> bool:
        """Elimina documentos por ID."""
        try:
            self.collection.delete(ids=ids)
            logger.info("Delete OK: %d id(s)", len(ids))
            return True
        except ChromaError as e:
            logger.error("Fallo el delete en ChromaDB (%s): %s", type(e).__name__, e)
            return False

    def count(self) -> int:
        """Cantidad de documentos actualmente en la coleccion."""
        return self.collection.count()


if __name__ == "__main__":
    manager = VectorMemoryManager(persist_path="./chroma_demo", collection_name="demo")

    # IDs deterministicos (estructurados, no aleatorios) para que un upsert
    # posterior con el mismo ID actualice el documento en vez de duplicarlo.
    ids = ["doc_001", "doc_002", "doc_003"]
    documents = [
        "Docker empaqueta aplicaciones en contenedores portables.",
        "Kubernetes orquesta el despliegue de contenedores en produccion.",
        "PostgreSQL es un motor de base de datos relacional de codigo abierto.",
    ]
    metadatas = [{"topic": "contenedores"}, {"topic": "contenedores"}, {"topic": "bases de datos"}]

    manager.upsert_documents(ids, documents, metadatas)
    print(f"Documentos en la coleccion: {manager.count()}")

    resultados = manager.semantic_search("como se organizan los contenedores en produccion", n_results=2)
    print("\nResultados de busqueda semantica:")
    for r in resultados:
        print(f"  [{r['id']}] distancia={r['distance']:.4f} -> {r['document']}")

    manager.delete_by_id(["doc_003"])
    print(f"\nDocumentos despues del delete: {manager.count()}")
