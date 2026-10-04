"""Agente de Analisis/Computo.

Herramienta: calculos matematicos sobre valores numericos ya extraidos
(normalmente, por el LLM del propio agente) del texto que trajo el
investigador. El LLM es responsable de convertir unidades heterogeneas a
una escala comun antes de llamar a la herramienta; la herramienta solo
hace la aritmetica.
"""

from typing import Any, List

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

ANALYST_SYSTEM_PROMPT = (
    "Sos el especialista de Analisis de un sistema multi-agente. Recibis "
    "texto o datos que el especialista de Investigacion ya encontro, y tu "
    "trabajo es procesarlos: si hay valores numericos en distintas "
    "unidades (ej. minutos, horas, dias habiles), convertilos vos mismo a "
    "una unidad comun ANTES de llamar a calcular_estadisticas (la "
    "herramienta no interpreta texto, solo hace la aritmetica). No "
    "inventes datos que no esten en lo que te paso el investigador."
)


@tool
def calcular_estadisticas(valores: List[float]) -> dict:
    """Calcula estadisticas basicas (promedio, minimo, maximo, suma,
    cantidad) sobre una lista de valores numericos ya en una unidad comun.

    Usa esta herramienta para resumir o combinar varios numeros (ej. varios
    tiempos de respuesta ya convertidos a horas). No convierte unidades ni
    interpreta texto: esperá una lista de numeros ya normalizados.
    """
    if not valores:
        return {"error": "La lista de valores esta vacia"}
    return {
        "promedio": sum(valores) / len(valores),
        "minimo": min(valores),
        "maximo": max(valores),
        "suma": sum(valores),
        "cantidad": len(valores),
    }


def build_analyst_agent(model: Any):
    """Arma el sub-agente de analisis con create_react_agent."""
    return create_react_agent(model, tools=[calcular_estadisticas], prompt=ANALYST_SYSTEM_PROMPT)
