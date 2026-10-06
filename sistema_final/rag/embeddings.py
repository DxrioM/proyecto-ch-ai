"""Adaptador LangChain para el modelo de embeddings local de la Fase 3.

langchain-pinecone (el paquete "oficial" sugerido por la consigna) todavia
no tiene build compatible con Python 3.14 en este entorno (depende de
simsimd<4.0, sin wheels para 3.14). En vez de instalar sentence-transformers
+ torch de nuevo (pesado, y redundante con lo que ya usa la Fase 3), este
adaptador envuelve el mismo DefaultEmbeddingFunction de Chroma (Sentence
Transformers all-MiniLM-L6-v2 via ONNX, 384 dimensiones, ya cacheado
localmente, sin API key) en la interfaz Embeddings de LangChain, para
poder usarlo con BM25Retriever/EnsembleRetriever y con el SDK nativo de
Pinecone (ver pinecone_retriever.py).
"""

from typing import List

from chromadb.utils import embedding_functions
from langchain_core.embeddings import Embeddings

# Debe coincidir exactamente con la dimension del indice de Pinecone
# (ver fase4_ejercicio_pinecone_setup/setup_infra.py).
EMBEDDING_DIMENSION = 384


class LocalChromaEmbeddings(Embeddings):
    """Embeddings 100% locales, sin API key, compatibles con la interfaz
    de LangChain (embed_documents / embed_query)."""

    def __init__(self):
        self._fn = embedding_functions.DefaultEmbeddingFunction()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # DefaultEmbeddingFunction devuelve numpy.float32; hay que castear
        # a float nativo de Python, si no el SDK de Pinecone no puede
        # serializar el vector a JSON al upsertear ("Type is not JSON
        # serializable: numpy.float32").
        return [[float(x) for x in vector] for vector in self._fn(texts)]

    def embed_query(self, text: str) -> List[float]:
        return [float(x) for x in self._fn([text])[0]]
