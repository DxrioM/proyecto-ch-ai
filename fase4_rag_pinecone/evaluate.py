"""Componente D - Fase 4: evaluate.py, Precision@k y Recall@k sobre un golden set.

Golden set: pares {"pregunta": ..., "documento_id_esperado": ...} con el
archivo fuente correcto conocido de antemano (ver golden_set.json).
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Protocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("evaluate")

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


class Retriever(Protocol):
    """Contrato minimo que evaluar() necesita de un sistema de
    recuperacion: alcanza con .retrieve(pregunta) -> lista de objetos con
    .metadata['source']. Permite testear la logica de metricas con un
    doble falso, sin depender de Pinecone."""

    top_k: int

    def retrieve(self, query: str) -> List[Any]: ...


def cargar_golden_set(path: Path = GOLDEN_SET_PATH) -> List[Dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluar(sistema: Retriever, golden_set: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calcula, para cada pregunta del golden set:

    - Recall@k: 1 si el documento esperado aparece entre los k
      recuperados, 0 si no (mide si el sistema "entrega el contexto
      necesario" al LLM).
    - Precision@k: que fraccion de los k recuperados pertenecen al
      documento esperado (mide cuanto ruido hay en lo recuperado).

    Devuelve el promedio de ambas metricas sobre todo el golden set, mas el
    detalle pregunta por pregunta.
    """
    recalls = []
    precisions = []
    detalle = []

    for caso in golden_set:
        pregunta = caso["pregunta"]
        esperado = caso["documento_id_esperado"]
        resultados = sistema.retrieve(pregunta)
        fuentes = [r.metadata.get("source") for r in resultados]

        acierto = esperado in fuentes
        recall = 1.0 if acierto else 0.0
        precision = fuentes.count(esperado) / len(fuentes) if fuentes else 0.0

        recalls.append(recall)
        precisions.append(precision)
        detalle.append(
            {
                "pregunta": pregunta,
                "esperado": esperado,
                "recuperados": fuentes,
                "recall": recall,
                "precision": precision,
            }
        )
        logger.info("[%s] %s -> recuperados=%s", "OK" if acierto else "MISS", pregunta, fuentes)

    return {
        "recall_at_k": sum(recalls) / len(recalls) if recalls else 0.0,
        "precision_at_k": sum(precisions) / len(precisions) if precisions else 0.0,
        "detalle": detalle,
    }


if __name__ == "__main__":
    from fase4_rag_pinecone.rag_system import RAGSystem

    sistema = RAGSystem()
    golden_set = cargar_golden_set()
    resumen = evaluar(sistema, golden_set)

    print(f"\nRecall@{sistema.top_k}: {resumen['recall_at_k']:.2f}")
    print(f"Precision@{sistema.top_k}: {resumen['precision_at_k']:.2f}")
    print("\nDetalle:")
    for d in resumen["detalle"]:
        veredicto = "OK" if d["recall"] else "MISS"
        print(f"  [{veredicto}] {d['pregunta']}")
        print(f"       esperado={d['esperado']}  recuperados={d['recuperados']}")
