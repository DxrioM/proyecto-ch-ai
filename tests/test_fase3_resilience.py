"""Tests sinteticos de resiliencia y casos limite para la Fase 3 (RAG local).

Mismo criterio que tests/test_fase2_resilience.py: no llaman a la API real
de Groq ni dependen de ChromaDB/tiktoken reales donde se puede evitar,
usando dobles falsos (RunnableLambda con with_retry() real, o clases fake
minimas) para ejercitar deterministicamente los caminos de error.

Cubre:
1. rag_chain.get_rag_response(): retry exitoso, retry agotado (sin crash,
   con fallback), ValidationError contenida.
2. VectorMemoryManager: upsert/query/delete devuelven un valor seguro
   (False/[]) cuando la coleccion de Chroma falla, en vez de propagar la
   excepcion.
3. ingest(): idempotencia real (un archivo sin cambios no dispara upsert) y
   la rama que borra chunks huerfanos cuando un archivo se achica -
   documentada en el README pero nunca antes ejercitada.
4. DocumentProcessor: casos limite (texto vacio, texto muy corto).
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List

import pytest
from chromadb.errors import ChromaError
from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError

import fase3_rag_local.ingest as ingest_module
from fase3_ejercicio_chunking.document_processor import DocumentProcessor
from fase3_ejercicio_chromadb.vector_memory_manager import VectorMemoryManager
from fase3_rag_local.rag_chain import RagResponse, get_rag_response

FAST_RETRY = {"initial": 0.01, "max": 0.05}

RAG_OK = RagResponse(respuesta="respuesta de prueba", fuentes=["doc.md"], encontrado_en_contexto=True)


class _FakeSearchManager:
    """VectorMemoryManager falso: semantic_search() devuelve un resultado fijo,
    para poder probar solo la capa de generacion de get_rag_response()."""

    def semantic_search(self, query_text: str, n_results: int = 4) -> List[Dict[str, Any]]:
        return [{"id": "doc_0", "document": "contenido de prueba", "metadata": {"source": "doc.md"}, "distance": 0.1}]


def _fake_runnable(action):
    calls = {"count": 0}

    async def _ainvoke(_input):
        calls["count"] += 1
        return action()

    return RunnableLambda(_ainvoke), calls


def _recovers_after(fail_times: int, success_value):
    state = {"n": 0}

    def action():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise ConnectionError("fallo transitorio de red simulado")
        return success_value

    return action


def _always_fails_with_network_error():
    def action():
        raise ConnectionError("caido a proposito, nunca se recupera")

    return action


# ---------------------------------------------------------------------------
# 1. rag_chain.get_rag_response()
# ---------------------------------------------------------------------------


def test_get_rag_response_retries_and_recovers():
    fake, calls = _fake_runnable(_recovers_after(fail_times=2, success_value=RAG_OK))
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(get_rag_response("pregunta", _FakeSearchManager(), chain=resilient))

    assert resultado == RAG_OK
    assert calls["count"] == 3


def test_get_rag_response_retry_exhausted_returns_fallback_without_crash():
    """Antes de este fix, get_rag_response() no atrapaba la excepcion y un
    fallo persistente de red rompia todo el script (a diferencia del resto
    del proyecto). Ahora debe devolver una RagResponse de fallback."""
    fake, calls = _fake_runnable(_always_fails_with_network_error())
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(get_rag_response("pregunta", _FakeSearchManager(), chain=resilient))

    assert resultado.encontrado_en_contexto is False
    assert resultado.fuentes == []
    assert calls["count"] == 3


def test_get_rag_response_validation_error_is_contained():
    def action_invalido():
        # encontrado_en_contexto es requerido (sin default): omitirlo
        # dispara ValidationError, igual que with_structured_output() ante
        # una respuesta del LLM incompleta o con tipos incorrectos.
        return RagResponse(respuesta="x", fuentes=["x"])  # falta encontrado_en_contexto

    fake, calls = _fake_runnable(action_invalido)
    resilient = fake.with_retry(
        stop_after_attempt=2,
        retry_if_exception_type=(ValidationError,),
        exponential_jitter_params=FAST_RETRY,
    )

    resultado = asyncio.run(get_rag_response("pregunta", _FakeSearchManager(), chain=resilient))

    assert resultado.encontrado_en_contexto is False
    assert calls["count"] == 2


# ---------------------------------------------------------------------------
# 2. VectorMemoryManager: manejo de errores de ChromaDB
# ---------------------------------------------------------------------------


class _FailingCollection:
    """Doble falso de una coleccion de Chroma que siempre falla, para
    probar que VectorMemoryManager nunca deja escapar un ChromaError."""

    def upsert(self, **kwargs):
        raise ChromaError("upsert simulado fallido")

    def query(self, **kwargs):
        raise ChromaError("query simulado fallido")

    def delete(self, **kwargs):
        raise ChromaError("delete simulado fallido")


@pytest.fixture
def manager_con_coleccion_rota(tmp_path: Path) -> VectorMemoryManager:
    manager = VectorMemoryManager(persist_path=str(tmp_path / "chroma"), collection_name="test_errores")
    manager.collection = _FailingCollection()
    return manager


def test_upsert_documents_returns_false_on_chroma_error(manager_con_coleccion_rota):
    ok = manager_con_coleccion_rota.upsert_documents(["id_1"], ["doc"], [{"source": "x"}])
    assert ok is False


def test_semantic_search_returns_empty_list_on_chroma_error(manager_con_coleccion_rota):
    resultados = manager_con_coleccion_rota.semantic_search("query cualquiera")
    assert resultados == []


def test_delete_by_id_returns_false_on_chroma_error(manager_con_coleccion_rota):
    ok = manager_con_coleccion_rota.delete_by_id(["id_1"])
    assert ok is False


# ---------------------------------------------------------------------------
# 3. ingest(): idempotencia real + limpieza de chunks huerfanos
# ---------------------------------------------------------------------------


class _FakeProcessor:
    """Fragmenta por '|' en vez de por tokens, para controlar exactamente
    cuantos chunks genera cada corrida sin depender de tiktoken."""

    def process_document(self, text: str) -> List[str]:
        return [c for c in text.split("|") if c]


class _FakeManager:
    def __init__(self):
        self.upserted: Dict[str, Any] = {}
        self.deleted_ids: List[str] = []
        self.upsert_calls = 0

    def upsert_documents(self, ids, documents, metadatas):
        self.upsert_calls += 1
        for i, d, m in zip(ids, documents, metadatas):
            self.upserted[i] = (d, m)
        return True

    def delete_by_id(self, ids):
        self.deleted_ids.extend(ids)
        for i in ids:
            self.upserted.pop(i, None)
        return True

    def count(self):
        return len(self.upserted)


def test_ingest_is_idempotent_skips_unchanged_files(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.md").write_text("chunk0|chunk1|chunk2", encoding="utf-8")

    fake_manager = _FakeManager()
    manifest_path = tmp_path / "vectorstore" / "manifest.json"

    ingest_module.ingest(
        data_dir=data_dir, manager=fake_manager, processor=_FakeProcessor(), manifest_path=manifest_path
    )
    assert fake_manager.upsert_calls == 1
    assert fake_manager.count() == 3

    # Segunda corrida, archivo sin cambios: no debe volver a upsertear nada.
    ingest_module.ingest(
        data_dir=data_dir, manager=fake_manager, processor=_FakeProcessor(), manifest_path=manifest_path
    )
    assert fake_manager.upsert_calls == 1  # sigue en 1, no aumento


def test_ingest_deletes_orphaned_chunks_when_file_shrinks(tmp_path: Path):
    """Rama documentada en el README pero nunca antes ejercitada: si un
    archivo cambia y genera MENOS chunks que la version anterior, ingest()
    debe borrar los IDs viejos que sobran."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    doc_path = data_dir / "doc.md"
    doc_path.write_text("chunk0|chunk1|chunk2", encoding="utf-8")

    fake_manager = _FakeManager()
    manifest_path = tmp_path / "vectorstore" / "manifest.json"

    ingest_module.ingest(
        data_dir=data_dir, manager=fake_manager, processor=_FakeProcessor(), manifest_path=manifest_path
    )
    assert set(fake_manager.upserted.keys()) == {"doc_0", "doc_1", "doc_2"}

    # El archivo se achica: ahora genera un solo chunk.
    doc_path.write_text("chunk0only", encoding="utf-8")

    ingest_module.ingest(
        data_dir=data_dir, manager=fake_manager, processor=_FakeProcessor(), manifest_path=manifest_path
    )

    assert "doc_1" in fake_manager.deleted_ids
    assert "doc_2" in fake_manager.deleted_ids
    assert set(fake_manager.upserted.keys()) == {"doc_0"}
    assert fake_manager.count() == 1


# ---------------------------------------------------------------------------
# 4. DocumentProcessor: casos limite
# ---------------------------------------------------------------------------


def test_document_processor_empty_text_returns_no_chunks():
    processor = DocumentProcessor()
    chunks = processor.process_document("")
    assert chunks == []


def test_document_processor_short_text_returns_single_chunk():
    processor = DocumentProcessor()
    chunks = processor.process_document("Una oracion corta de prueba.")
    assert len(chunks) == 1
    assert "oracion corta" in chunks[0]
