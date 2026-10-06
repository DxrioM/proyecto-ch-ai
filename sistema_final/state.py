"""Fase 6: esquema de estado compartido del orquestador multi-agente.

Hereda de MessagesState (lista de mensajes con el reducer add_messages) y
agrega los campos que el Supervisor necesita para rutear dinamicamente, y
una lista de "contribuciones" que registra que especialista aporto que
informacion - evita perder el rastro de quien dijo que en una
conversacion con varios agentes.
"""

import operator
from typing import Annotated, List, Literal, Optional, TypedDict

from langgraph.graph import MessagesState

NextAgent = Literal["investigador", "analista", "FINISH"]


class Contribucion(TypedDict):
    """Un aporte de un especialista, para rastrear quien dijo que."""

    agente: str
    resumen: str


class OrchestratorState(MessagesState):
    """Estado compartido entre el Supervisor y los especialistas.

    next_agent: a quien rutea la proxima arista condicional (lo decide el
      nodo Supervisor en cada paso).
    task_completed: True una vez que el Supervisor decide finalizar.
    contribuciones: acumula (via operator.add, nunca se sobreescribe) un
      resumen de que aporto cada especialista, en orden - la forma
      concreta en la que este orquestador evita "perder el contexto en la
      comunicacion asincrona" que pide la consigna.
    """

    next_agent: Optional[NextAgent]
    task_completed: bool
    contribuciones: Annotated[List[Contribucion], operator.add]
