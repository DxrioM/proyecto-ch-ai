"""Tests sinteticos para la Fase 4 (Pinecone, ingesta masiva, RAG hibrido).

No requieren PINECONE_API_KEY ni conexion real: usan el MockPineconeIndex
del propio Componente B y dobles falsos con la misma forma que el SDK
real, siguiendo el mismo criterio que tests/test_fase3_resilience.py.

Cubre:
1. IngestionPipeline (Componente B): batching correcto, filtrado por
   categoria, snippet de texto configurable, id_generator inyectable.
2. PineconeRetriever: arma Document de LangChain a partir de una respuesta
   con la misma forma que pinecone.Index.query().
3. evaluate.evaluar(): Recall@k/Precision@k con un sistema perfecto, uno
   que siempre falla y uno parcialmente correcto.
4. ingest() (Fase 4): idempotencia real y limpieza de chunks huerfanos,
   igual que se probo para fase3_rag_local/ingest.py.
"""

import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

from fase4_ejercicio_ingesta_masiva.ingestion_pipeline import IngestionPipeline, MockPineconeIndex
from fase4_rag_pinecone.evaluate import evaluar
from fase4_rag_pinecone.pinecone_retriever import PineconeRetriever


# ---------------------------------------------------------------------------
# 1. IngestionPipeline (Componente B)
# ---------------------------------------------------------------------------


def test_process_and_upsert_batches_splits_correctly():
    index = MockPineconeIndex()
    pipeline = IngestionPipeline(index, batch_size=2)
    documentos = [
        {"text": f"documento {i}", "embedding": [0.1, 0.2], "category": "cat", "author": "autor"}
        for i in range(5)
    ]

    total = asyncio.run(pipeline.process_and_upsert_batches(documentos))

    assert total == 5
    assert len(index.vectors) == 5


def test_search_by_category_filters_correctly():
    index = MockPineconeIndex()
    pipeline = IngestionPipeline(index)
    documentos = [
        {"text": "doc infra", "embedding": [0.1], "category": "infraestructura", "author": "a"},
        {"text": "doc seguridad", "embedding": [0.2], "category": "seguridad", "author": "a"},
    ]
    asyncio.run(pipeline.process_and_upsert_batches(documentos))

    resultados = asyncio.run(pipeline.search_by_category([0.1], category="infraestructura"))

    assert len(resultados) == 1
    assert resultados[0]["metadata"]["category"] == "infraestructura"


def test_create_metadata_snippet_length_is_configurable():
    texto_largo = "x" * 500

    pipeline_default = IngestionPipeline(MockPineconeIndex())  # default: snippet de 100
    metadata_default = pipeline_default.create_metadata(texto_largo, "cat", "autor")
    assert len(metadata_default["text"]) == 100
    assert metadata_default["char_count"] == 500

    pipeline_completo = IngestionPipeline(MockPineconeIndex(), text_snippet_length=None)
    metadata_completa = pipeline_completo.create_metadata(texto_largo, "cat", "autor")
    assert len(metadata_completa["text"]) == 500


def test_process_and_upsert_batches_uses_custom_id_generator():
    index = MockPineconeIndex()
    pipeline = IngestionPipeline(index)
    documentos = [
        {"text": "a", "embedding": [0.1], "category": "cat", "author": "autor", "mi_id": "doc_a"},
        {"text": "b", "embedding": [0.2], "category": "cat", "author": "autor", "mi_id": "doc_b"},
    ]

    asyncio.run(
        pipeline.process_and_upsert_batches(documentos, id_generator=lambda i, doc: doc["mi_id"])
    )

    assert set(index.vectors.keys()) == {"doc_a", "doc_b"}


# ---------------------------------------------------------------------------
# 2. PineconeRetriever
# ---------------------------------------------------------------------------


class _FakeEmbeddings:
    def embed_query(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3]


class _FakeIndex:
    def query(self, vector, top_k, namespace, filter, include_metadata):
        match = SimpleNamespace(
            id="doc_0", score=0.9, metadata={"text": "contenido de prueba", "source": "arquitectura.md"}
        )
        return SimpleNamespace(matches=[match])


def test_pinecone_retriever_builds_documents_from_matches():
    retriever = PineconeRetriever(index=_FakeIndex(), embeddings=_FakeEmbeddings(), namespace="test", top_k=3)

    documentos = retriever.invoke("pregunta de prueba")

    assert len(documentos) == 1
    assert documentos[0].page_content == "contenido de prueba"
    assert documentos[0].metadata["source"] == "arquitectura.md"
    assert "text" not in documentos[0].metadata  # se extrae a page_content, no queda duplicado


# ---------------------------------------------------------------------------
# 3. evaluate.evaluar()
# ---------------------------------------------------------------------------

_GOLDEN_SET_DE_PRUEBA = [
    {"pregunta": "pregunta 1", "documento_id_esperado": "a.md"},
    {"pregunta": "pregunta 2", "documento_id_esperado": "b.md"},
]


class _SistemaPerfecto:
    top_k = 5

    def retrieve(self, query):
        esperado = "a.md" if query == "pregunta 1" else "b.md"
        return [SimpleNamespace(metadata={"source": esperado})] + [
            SimpleNamespace(metadata={"source": "otro.md"})
        ] * 4


class _SistemaSiempreFalla:
    top_k = 5

    def retrieve(self, query):
        return [SimpleNamespace(metadata={"source": "irrelevante.md"})] * 5


def test_evaluar_sistema_perfecto():
    resumen = evaluar(_SistemaPerfecto(), _GOLDEN_SET_DE_PRUEBA)
    assert resumen["recall_at_k"] == 1.0
    assert resumen["precision_at_k"] == 0.2  # 1 de 5 recuperados es el correcto


def test_evaluar_sistema_que_siempre_falla():
    resumen = evaluar(_SistemaSiempreFalla(), _GOLDEN_SET_DE_PRUEBA)
    assert resumen["recall_at_k"] == 0.0
    assert resumen["precision_at_k"] == 0.0


# ---------------------------------------------------------------------------
# 4. fase4_rag_pinecone.ingest(): idempotencia + limpieza de chunks huerfanos
# ---------------------------------------------------------------------------


class _FakeProcessor:
    def process_document(self, text: str) -> List[str]:
        return [c for c in text.split("|") if c]


class _FakeEmbeddingsBatch:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1, 0.2] for _ in texts]


class _FakeAdapter:
    """Doble falso con la misma interfaz que PineconeAsyncAdapter."""

    def __init__(self):
        self.vectors: Dict[str, Any] = {}
        self.deleted_ids: List[str] = []
        self.upsert_calls = 0

    async def upsert(self, vectors: List[dict]) -> dict:
        self.upsert_calls += 1
        for v in vectors:
            self.vectors[v["id"]] = v
        return {"upserted_count": len(vectors)}

    async def delete(self, ids: List[str]) -> None:
        self.deleted_ids.extend(ids)
        for i in ids:
            self.vectors.pop(i, None)


def _run_ingest(data_dir: Path, manifest_path: Path, chunks_cache_path: Path, adapter: _FakeAdapter):
    import fase4_rag_pinecone.ingest as ingest_module

    pipeline = IngestionPipeline(adapter, text_snippet_length=None)
    return asyncio.run(
        ingest_module.ingest(
            data_dir=data_dir,
            manifest_path=manifest_path,
            chunks_cache_path=chunks_cache_path,
            pipeline=pipeline,
            embeddings=_FakeEmbeddingsBatch(),
            processor=_FakeProcessor(),
        )
    )


def test_fase4_ingest_is_idempotent(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.md").write_text("chunk0|chunk1|chunk2", encoding="utf-8")

    manifest_path = tmp_path / "vectorstore" / "manifest.json"
    chunks_cache_path = tmp_path / "vectorstore" / "chunks_cache.json"
    adapter = _FakeAdapter()

    _run_ingest(data_dir, manifest_path, chunks_cache_path, adapter)
    assert adapter.upsert_calls == 1
    assert len(adapter.vectors) == 3

    _run_ingest(data_dir, manifest_path, chunks_cache_path, adapter)
    assert adapter.upsert_calls == 1  # sin cambios, no vuelve a upsertear


def test_fase4_ingest_deletes_orphaned_chunks_when_file_shrinks(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    doc_path = data_dir / "doc.md"
    doc_path.write_text("chunk0|chunk1|chunk2", encoding="utf-8")

    manifest_path = tmp_path / "vectorstore" / "manifest.json"
    chunks_cache_path = tmp_path / "vectorstore" / "chunks_cache.json"
    adapter = _FakeAdapter()

    _run_ingest(data_dir, manifest_path, chunks_cache_path, adapter)
    assert set(adapter.vectors.keys()) == {"doc_0", "doc_1", "doc_2"}

    doc_path.write_text("chunk0only", encoding="utf-8")
    chunks_indexados = _run_ingest(data_dir, manifest_path, chunks_cache_path, adapter)

    assert "doc_1" in adapter.deleted_ids
    assert "doc_2" in adapter.deleted_ids
    assert set(adapter.vectors.keys()) == {"doc_0"}
    assert len(chunks_indexados) == 1
