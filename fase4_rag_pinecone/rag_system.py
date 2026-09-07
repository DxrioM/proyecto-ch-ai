"""Componente D - Fase 4: RAGSystem, recuperador hibrido (Pinecone + BM25).

Combina busqueda vectorial (semantica, via Pinecone) con busqueda lexica
(BM25, local) usando EnsembleRetriever, para mejorar la precision en
terminos tecnicos o nombres propios que un embedding puede diluir
semanticamente (ver fase4_metricas_recuperacion_hibrida/README.md).
"""

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from pinecone import Pinecone

from fase4_ejercicio_pinecone_setup.setup_infra import DEFAULT_DIMENSION
from fase4_rag_pinecone.embeddings import LocalChromaEmbeddings
from fase4_rag_pinecone.ingest import CHUNKS_CACHE_PATH, INDEX_NAME, NAMESPACE
from fase4_rag_pinecone.pinecone_retriever import PineconeRetriever

TOP_K = 5


def build_bm25_retriever(chunks_cache_path: Path = CHUNKS_CACHE_PATH, top_k: int = TOP_K) -> BM25Retriever:
    """Arma el retriever lexico local a partir del cache de chunks que deja
    ingest() (evita releer y refragmentar los archivos fuente)."""
    if not chunks_cache_path.exists():
        raise ValueError(
            f"No se encontro {chunks_cache_path}. Corre 'python -m fase4_rag_pinecone.ingest' primero."
        )
    chunks = json.loads(chunks_cache_path.read_text(encoding="utf-8"))
    documentos = [Document(page_content=c["text"], metadata=c["metadata"]) for c in chunks]
    retriever = BM25Retriever.from_documents(documentos)
    retriever.k = top_k
    return retriever


class RAGSystem:
    """Recuperador hibrido: EnsembleRetriever fusiona un retriever
    vectorial (Pinecone) con uno lexico (BM25 local)."""

    def __init__(self, top_k: int = TOP_K, chunks_cache_path: Path = CHUNKS_CACHE_PATH):
        load_dotenv()
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("Falta PINECONE_API_KEY en .env")

        pc = Pinecone(api_key=api_key)
        index = pc.Index(INDEX_NAME)
        embeddings = LocalChromaEmbeddings()

        vector_retriever = PineconeRetriever(
            index=index, embeddings=embeddings, namespace=NAMESPACE, top_k=top_k
        )
        bm25_retriever = build_bm25_retriever(chunks_cache_path, top_k)

        # Pesos iguales: ninguna de las dos senales (semantica/lexica)
        # domina por defecto. EnsembleRetriever fusiona ambos rankings por
        # posicion, equivalente en espiritu a Reciprocal Rank Fusion.
        self.retriever = EnsembleRetriever(retrievers=[vector_retriever, bm25_retriever], weights=[0.5, 0.5])
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Document]:
        """Recupera hasta top_k documentos combinando busqueda vectorial y
        lexica."""
        return self.retriever.invoke(query)[: self.top_k]


if __name__ == "__main__":
    sistema = RAGSystem()
    resultados = sistema.retrieve("Que base de datos usa el sistema de pedidos?")
    print(f"Top {len(resultados)} resultados (hibrido Pinecone + BM25):")
    for doc in resultados:
        print(f"  [{doc.metadata.get('source')}] {doc.page_content[:80]}...")
