"""Retriever vectorial propio sobre el SDK nativo de Pinecone.

Sustituye a langchain-pinecone (PineconeVectorStore), que todavia no tiene
build compatible con Python 3.14 en este entorno (ver embeddings.py).
Implementa el contrato minimo de BaseRetriever de LangChain para poder
combinarse con BM25Retriever dentro de un EnsembleRetriever, igual que si
se hubiera usado el paquete oficial.
"""

from typing import Any, List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pinecone import Index

from fase4_rag_pinecone.embeddings import LocalChromaEmbeddings


class PineconeRetriever(BaseRetriever):
    """Busca por similitud vectorial en un indice Pinecone y devuelve
    Document de LangChain, con el texto original recuperado desde la
    metadata (para no depender de otra base de datos)."""

    index: Any
    embeddings: Any
    namespace: str = "fase4-corpus"
    top_k: int = 5
    filter: Optional[dict] = None

    def __init__(
        self,
        index: Index,
        embeddings: LocalChromaEmbeddings,
        namespace: str = "fase4-corpus",
        top_k: int = 5,
        filter: Optional[dict] = None,
    ):
        super().__init__(index=index, embeddings=embeddings, namespace=namespace, top_k=top_k, filter=filter)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        vector = self.embeddings.embed_query(query)
        resultado = self.index.query(
            vector=vector,
            top_k=self.top_k,
            namespace=self.namespace,
            filter=self.filter,
            include_metadata=True,
        )
        documentos = []
        for match in resultado.matches:
            metadata = dict(match.metadata or {})
            texto = metadata.pop("text", "")
            metadata["score"] = match.score
            metadata["id"] = match.id
            documentos.append(Document(page_content=texto, metadata=metadata))
        return documentos
