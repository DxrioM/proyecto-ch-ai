"""Recuperador hibrido del Sistema Final: Pinecone (semantico) + BM25 (lexico).

EnsembleRetriever fusiona ambos rankings por posicion (equivalente en
espiritu a Reciprocal Rank Fusion). La busqueda vectorial usa el SDK
sincrono de Pinecone; LangChain la ejecuta en un thread al llamar
ainvoke, asi que el event loop nunca se bloquea.
"""

import json
import os
from pathlib import Path
from typing import List

from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from pinecone import Pinecone

from sistema_final.config import PINECONE_INDEX_NAME, PINECONE_NAMESPACE, PINECONE_TOP_K, get_required
from sistema_final.rag.embeddings import LocalChromaEmbeddings
from sistema_final.rag.ingest import CHUNKS_CACHE_PATH
from sistema_final.rag.pinecone_retriever import PineconeRetriever


def build_bm25_retriever(chunks_cache_path: Path = CHUNKS_CACHE_PATH, top_k: int = PINECONE_TOP_K) -> BM25Retriever:
    """Arma el retriever lexico a partir del cache de chunks que deja la
    ingesta (evita releer y refragmentar los archivos fuente)."""
    if not chunks_cache_path.exists():
        raise ValueError(
            f"No se encontro {chunks_cache_path}. Corre 'python -m sistema_final.rag.ingest' primero."
        )
    chunks = json.loads(chunks_cache_path.read_text(encoding="utf-8"))
    documentos = [Document(page_content=c["text"], metadata=c["metadata"]) for c in chunks]
    retriever = BM25Retriever.from_documents(documentos)
    retriever.k = top_k
    return retriever


class HybridRAG:
    """Busqueda hibrida sobre el corpus indexado. Se construye una sola vez
    (ver get_rag) porque abrir el indice y el modelo de embeddings es caro."""

    def __init__(self, top_k: int = PINECONE_TOP_K, chunks_cache_path: Path = CHUNKS_CACHE_PATH):
        api_key = get_required("PINECONE_API_KEY")
        index = Pinecone(api_key=api_key).Index(PINECONE_INDEX_NAME)
        vector_retriever = PineconeRetriever(
            index=index,
            embeddings=LocalChromaEmbeddings(),
            namespace=PINECONE_NAMESPACE,
            top_k=top_k,
        )
        bm25_retriever = build_bm25_retriever(chunks_cache_path, top_k)
        # Pesos iguales: ninguna senal (semantica/lexica) domina por defecto.
        self.retriever = EnsembleRetriever(retrievers=[vector_retriever, bm25_retriever], weights=[0.5, 0.5])
        self.top_k = top_k

    async def aretrieve(self, query: str) -> List[Document]:
        """Recupera hasta top_k documentos combinando busqueda vectorial y
        lexica, sin bloquear el event loop."""
        documentos = await self.retriever.ainvoke(query)
        return documentos[: self.top_k]


_rag: HybridRAG | None = None


def get_rag() -> HybridRAG:
    """Singleton de vida larga para el recuperador hibrido."""
    global _rag
    if _rag is None:
        _rag = HybridRAG()
    return _rag
