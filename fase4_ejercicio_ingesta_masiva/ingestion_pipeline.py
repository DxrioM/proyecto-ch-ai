"""Componente B - Fase 4: Ingesta masiva y gestion de metadatos avanzados.

Pipeline de ingesta con batching y metadatos enriquecidos, sobre un mock de
indice (no requiere cuenta real de Pinecone). El mismo IngestionPipeline se
reutiliza en fase4_rag_pinecone/ingest.py contra un indice Pinecone real.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("ingestion_pipeline")


class MockPineconeIndex:
    """Doble falso de un indice Pinecone, para desarrollar y testear el
    pipeline sin depender de una cuenta real."""

    def __init__(self):
        self.vectors: Dict[str, Dict[str, Any]] = {}

    async def upsert(self, vectors: List[Dict]) -> Dict[str, int]:
        for v in vectors:
            self.vectors[v["id"]] = v
        return {"upserted_count": len(vectors)}

    async def query(self, vector: List[float], top_k: int, filter: Optional[Dict] = None) -> Dict[str, list]:
        # Mock simple: no calcula similitud real, solo aplica el filtro de
        # metadatos ($eq) para simular una busqueda filtrada por categoria.
        candidatos = list(self.vectors.values())
        if filter:
            for campo, condicion in filter.items():
                valor_esperado = condicion.get("$eq")
                candidatos = [v for v in candidatos if v["metadata"].get(campo) == valor_esperado]
        return {"matches": candidatos[:top_k]}


class IngestionPipeline:
    """Encapsula la ingesta masiva: metadatos enriquecidos + batching +
    busqueda filtrada por categoria."""

    def __init__(self, index: MockPineconeIndex, batch_size: int = 100, text_snippet_length: Optional[int] = 100):
        self.index = index
        self.batch_size = batch_size
        # None = guardar el texto completo en metadata (necesario si este
        # es el unico lugar donde se persiste el contenido, como en
        # fase4_rag_pinecone). El default (100) matchea el enunciado
        # original del ejercicio: un snippet corto alcanza para mostrar
        # contexto sin inflar el tamano del vector.
        self.text_snippet_length = text_snippet_length

    def create_metadata(self, doc_text: str, category: str, author: str) -> Dict[str, Any]:
        """Arma los metadatos enriquecidos de un documento.

        Guardar el texto (completo o un snippet, segun text_snippet_length)
        dentro de la metadata evita tener que consultar otra base de datos
        relacional solo para mostrar o reconstruir el contenido.
        """
        texto = doc_text if self.text_snippet_length is None else doc_text[: self.text_snippet_length]
        return {
            "text": texto,
            "category": category,
            "author": author,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "char_count": len(doc_text),
        }

    async def process_and_upsert_batches(
        self,
        documents: List[Dict],
        batch_size: Optional[int] = None,
        id_generator: Optional[Callable[[int, Dict[str, Any]], str]] = None,
    ) -> int:
        """Divide documents en batches y hace upsert de a lotes (nunca
        vector por vector: 100-200 por batch es el punto dulce entre
        latencia y estabilidad).

        Cada documento en `documents` debe tener al menos:
        {"text": str, "embedding": List[float], "category": str, "author": str}

        id_generator es inyectable (recibe el indice global del documento y
        el documento mismo, debe devolver un str) para poder usar IDs
        deterministicos en vez de uuid4 al azar cuando hace falta ingesta
        idempotente (ver fase4_rag_pinecone/ingest.py). Por defecto usa
        uuid4, igual que la solucion de referencia del ejercicio.
        """
        batch_size = batch_size or self.batch_size
        id_generator = id_generator or (lambda indice, doc: str(uuid.uuid4()))
        total_upserted = 0

        for i in range(0, len(documents), batch_size):
            lote = documents[i : i + batch_size]
            vectores_a_subir = [
                {
                    "id": id_generator(i + j, doc),
                    "values": doc["embedding"],
                    "metadata": self.create_metadata(doc["text"], doc["category"], doc["author"]),
                }
                for j, doc in enumerate(lote)
            ]
            resultado = await self.index.upsert(vectores_a_subir)
            total_upserted += resultado["upserted_count"]
            logger.info(
                "Batch %d-%d: %d vectores upserteados", i, i + len(lote), resultado["upserted_count"]
            )

        logger.info("Ingesta completa: %d vectores en total", total_upserted)
        return total_upserted

    async def search_by_category(self, query_vector: List[float], category: str, top_k: int = 5) -> List[Dict]:
        """Busqueda vectorial acotada por categoria, usando el operador de
        filtro $eq para reducir el espacio de busqueda antes de rankear."""
        resultado = await self.index.query(vector=query_vector, top_k=top_k, filter={"category": {"$eq": category}})
        return resultado["matches"]


if __name__ == "__main__":

    async def main() -> None:
        index = MockPineconeIndex()
        pipeline = IngestionPipeline(index, batch_size=2)

        # Embeddings de juguete (vectores cortos) solo para demostrar el
        # flujo de batching y metadatos; en fase4_rag_pinecone se usan
        # embeddings reales.
        documentos = [
            {"text": "Guia de instalacion de FastAPI paso a paso.", "embedding": [0.1, 0.2, 0.3], "category": "infraestructura", "author": "equipo-backend"},
            {"text": "Politica de seguridad para el manejo de API keys.", "embedding": [0.4, 0.1, 0.2], "category": "seguridad", "author": "equipo-seguridad"},
            {"text": "Como configurar el autoscaling en Kubernetes.", "embedding": [0.2, 0.3, 0.1], "category": "infraestructura", "author": "equipo-backend"},
            {"text": "Checklist de auditoria de dependencias.", "embedding": [0.3, 0.4, 0.2], "category": "seguridad", "author": "equipo-seguridad"},
            {"text": "Runbook de rollback de despliegues fallidos.", "embedding": [0.15, 0.25, 0.35], "category": "infraestructura", "author": "equipo-backend"},
        ]

        await pipeline.process_and_upsert_batches(documentos)
        print(f"\nVectores en el indice mock: {len(index.vectors)}")

        resultados = await pipeline.search_by_category([0.1, 0.2, 0.3], category="infraestructura")
        print(f"\nResultados filtrados por categoria 'infraestructura' ({len(resultados)}):")
        for r in resultados:
            print(f"  [{r['id'][:8]}] {r['metadata']['text']}")

    asyncio.run(main())
