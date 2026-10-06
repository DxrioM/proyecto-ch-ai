"""Fase 7: Human-in-the-loop (HITL).

Define que se considera una accion "critica" en este sistema, y el payload
que se le muestra al humano para decidir si aprobarla.

Criterio de criticidad elegido para esta demo: cualquier pregunta que
requiera que el especialista de Analisis ejecute un calculo (en este
dominio, podria representar algo con costo real - ej. calcular una
penalidad de SLA o un reembolso) pasa por una pausa de aprobacion humana
antes de que el Analista corra. Las preguntas que solo necesitan
investigacion (sin calculo) nunca pasan por el gate - no tiene sentido
pedirle aprobacion humana a una busqueda de solo lectura.
"""

from typing import Any, Dict

ACCION_CRITICA = "ejecutar_analista"


def construir_payload_aprobacion(pregunta: str, hallazgos_investigador: str) -> Dict[str, Any]:
    """Arma el payload que se persiste en el checkpoint cuando el grafo se
    interrumpe, y que el cliente ve via GET /tasks/{id} mientras espera
    aprobacion."""
    return {
        "accion": ACCION_CRITICA,
        "motivo": (
            "La tarea requiere que el especialista de Analisis procese datos "
            "numericos (calculo con costo/impacto potencial) - requiere "
            "aprobacion humana antes de ejecutarse."
        ),
        "pregunta_original": pregunta,
        "datos_investigados": hallazgos_investigador,
    }
