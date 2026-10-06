"""Agente de Analisis/Computo.

Herramienta: calculos matematicos sobre valores numericos ya extraidos del
texto que trajo el investigador. El LLM convierte las unidades a una escala
comun antes de llamar a la herramienta; la herramienta solo hace la
aritmetica, y valida su entrada con Pydantic antes de calcular.
"""

import math
from typing import Any, List

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field, field_validator

ANALYST_SYSTEM_PROMPT = (
    "Sos el especialista de Analisis de un sistema multi-agente. Recibis "
    "texto o datos que el especialista de Investigacion ya encontro, y tu "
    "trabajo es procesarlos: si hay valores numericos en distintas "
    "unidades (ej. minutos, horas, dias habiles), convertilos vos mismo a "
    "una unidad comun ANTES de llamar a calcular_estadisticas (la "
    "herramienta no interpreta texto, solo hace la aritmetica). No "
    "inventes datos que no esten en lo que te paso el investigador."
)


class CalcularEstadisticasInput(BaseModel):
    """Entrada validada de calcular_estadisticas."""

    valores: List[float] = Field(min_length=1, max_length=500, description="Numeros ya en una unidad comun")

    @field_validator("valores")
    @classmethod
    def _solo_finitos(cls, valores: List[float]) -> List[float]:
        if not all(math.isfinite(v) for v in valores):
            raise ValueError("Todos los valores deben ser numeros finitos (sin NaN ni infinito)")
        return valores


@tool(args_schema=CalcularEstadisticasInput)
def calcular_estadisticas(valores: List[float]) -> dict:
    """Calcula estadisticas basicas (promedio, minimo, maximo, suma,
    cantidad) sobre una lista de valores numericos ya en una unidad comun.

    Usa esta herramienta para resumir o combinar varios numeros (ej. varios
    tiempos de respuesta ya convertidos a horas). No convierte unidades ni
    interpreta texto: esperá una lista de numeros ya normalizados.
    """
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
