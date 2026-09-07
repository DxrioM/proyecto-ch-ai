"""Componente A - Fase 3: Embeddings y Similitud, la geometria del lenguaje.

Calcula embeddings reales (el mismo modelo local que usa ChromaDB en los
Componentes C y D: Sentence Transformers all-MiniLM-L6-v2 via ONNX, sin API
key) para 5 oraciones semanticamente equivalentes sobre "despliegue de
microservicios" con vocabulario distinto entre si, mas 2 oraciones trampa
que comparten palabras clave pero significan algo totalmente distinto.

Calcula la Similitud Coseno entre todos los pares con scikit-learn, para
demostrar que el embedding agrupa por significado y no por coincidencia
lexica superficial.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
from chromadb.utils import embedding_functions
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("embeddings_similitud")

# 5 oraciones sobre el mismo concepto tecnico ("despliegue independiente de
# microservicios"), cada una con vocabulario distinto (sinonimia), evitando
# repetir las mismas palabras clave entre si.
ORACIONES_CONCEPTO: Dict[str, str] = {
    "concepto_1": (
        "Publicar cada componente del sistema por separado en produccion "
        "reduce el riesgo de una actualizacion global fallida."
    ),
    "concepto_2": (
        "La orquestacion de contenedores permite que distintos servicios se "
        "actualicen de forma independiente sin afectar al resto de la "
        "aplicacion."
    ),
    "concepto_3": (
        "Empaquetar la logica de negocio en unidades autonomas facilita "
        "liberar nuevas versiones sin detener el resto de la plataforma."
    ),
    "concepto_4": (
        "Cada modulo del backend se libera segun su propio ciclo, "
        "minimizando el impacto de una falla puntual en produccion."
    ),
    "concepto_5": (
        "El equipo de infraestructura promueve builds independientes por "
        "servicio para acelerar la entrega continua."
    ),
}

# 2 oraciones trampa: comparten palabras clave con las anteriores
# ("servicio", "micro", "contenedores", "despliegan") pero tratan un tema
# completamente distinto e irrelevante.
ORACIONES_TRAMPA: Dict[str, str] = {
    "trampa_1": (
        "El servicio de micro-limpieza del edificio es excelente y siempre "
        "llega puntual."
    ),
    "trampa_2": (
        "Los contenedores de reciclaje del barrio se despliegan cada lunes "
        "en la vereda."
    ),
}


def calcular_embeddings(oraciones: List[str]) -> np.ndarray:
    """Genera embeddings reales con el mismo modelo local que usan los
    Componentes C y D (DefaultEmbeddingFunction de Chroma)."""
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    vectores = embedding_fn(oraciones)
    return np.array(vectores)


def analizar() -> Tuple[List[str], List[str], np.ndarray]:
    """Calcula la matriz de similitud coseno entre las 7 oraciones y
    devuelve (labels, textos, matriz)."""
    labels = list(ORACIONES_CONCEPTO.keys()) + list(ORACIONES_TRAMPA.keys())
    textos = list(ORACIONES_CONCEPTO.values()) + list(ORACIONES_TRAMPA.values())

    logger.info("Calculando embeddings para %d oraciones...", len(textos))
    vectores = calcular_embeddings(textos)

    matriz = cosine_similarity(vectores)
    return labels, textos, matriz


def resumen(labels: List[str], matriz: np.ndarray) -> Dict[str, float]:
    """Compara la similitud promedio DENTRO del cluster de concepto contra
    la similitud promedio de las trampas hacia ese mismo cluster."""
    n_concepto = len(ORACIONES_CONCEPTO)
    idx_concepto = list(range(n_concepto))
    idx_trampa = list(range(n_concepto, len(labels)))

    intra_concepto = [
        matriz[i][j] for i in idx_concepto for j in idx_concepto if i < j
    ]
    trampa_a_concepto = [matriz[i][j] for i in idx_trampa for j in idx_concepto]

    return {
        "similitud_promedio_intra_concepto": float(np.mean(intra_concepto)),
        "similitud_promedio_trampa_a_concepto": float(np.mean(trampa_a_concepto)),
    }


def comparacion_lexica_vs_semantica(labels: List[str], matriz: np.ndarray) -> List[Dict]:
    """La comparacion mas fina y honesta del ejercicio: para cada trampa,
    la enfrenta contra "concepto_2" (con quien comparte la palabra clave
    literal 'servicio'/'contenedores') y compara esa similitud puntual
    contra el promedio de concepto_2 con sus propios pares semanticos
    reales (concepto_1/3/4/5). Si el embedding entiende significado y no
    solo lexico, la trampa deberia score MENOS que ese promedio, pese a
    compartir la palabra clave."""
    idx = {label: i for i, label in enumerate(labels)}
    idx_ref = idx["concepto_2"]  # comparte "servicio(s)" y "contenedores" con ambas trampas
    idx_pares = [idx[f"concepto_{n}"] for n in (1, 3, 4, 5)]

    promedio_pares_reales = float(np.mean([matriz[idx_ref][j] for j in idx_pares]))

    filas = []
    for trampa_label in ORACIONES_TRAMPA:
        sim_trampa = float(matriz[idx[trampa_label]][idx_ref])
        filas.append(
            {
                "trampa": trampa_label,
                "similitud_vs_concepto_2": sim_trampa,
                "promedio_concepto_2_vs_sus_pares_reales": promedio_pares_reales,
                "menor_pese_a_palabra_compartida": sim_trampa < promedio_pares_reales,
            }
        )
    return filas


if __name__ == "__main__":
    labels, textos, matriz = analizar()

    print("\nMatriz de similitud coseno:")
    header = "          " + " ".join(f"{l:>10}" for l in labels)
    print(header)
    for i, label in enumerate(labels):
        fila = " ".join(f"{matriz[i][j]:10.3f}" for j in range(len(labels)))
        print(f"{label:>10} {fila}")

    stats = resumen(labels, matriz)
    print("\nResumen:")
    print(f"  Similitud promedio ENTRE las 5 oraciones de concepto: {stats['similitud_promedio_intra_concepto']:.3f}")
    print(f"  Similitud promedio de las TRAMPAS hacia el concepto: {stats['similitud_promedio_trampa_a_concepto']:.3f}")

    if stats["similitud_promedio_intra_concepto"] > stats["similitud_promedio_trampa_a_concepto"]:
        print("\nOK: el embedding agrupa por significado, no por coincidencia lexica.")
    else:
        print("\nADVERTENCIA: las trampas resultaron mas similares que el propio cluster de concepto.")

    print("\nComparacion lexica vs. semantica (evidencia mas fina):")
    for fila in comparacion_lexica_vs_semantica(labels, matriz):
        veredicto = "OK" if fila["menor_pese_a_palabra_compartida"] else "ADVERTENCIA"
        print(
            f"  [{veredicto}] {fila['trampa']} vs concepto_2 (palabra compartida) = "
            f"{fila['similitud_vs_concepto_2']:.3f}  <  "
            f"promedio concepto_2 vs sus pares reales = "
            f"{fila['promedio_concepto_2_vs_sus_pares_reales']:.3f}"
        )
