"""Fase 6: demo del flujo de delegacion Supervisor -> Investigador -> Analista -> FINISH.

Lanza una consulta que obliga al Supervisor a:
1. Enviar la tarea al Investigador (falta informacion factual).
2. Recibir el dato investigado.
3. Enviarlo al Analista (hay que convertir unidades y calcular un promedio).
4. Cerrar la conversacion con una sintesis final (FINISH).

Guarda la traza completa (decisiones del supervisor + aportes de cada
especialista) en traces/ejemplo_flujo_delegacion.json.
"""

import asyncio
import json
import logging
from pathlib import Path

from langchain_core.messages import HumanMessage

from .graph import compile_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("fase6_main")

BASE_DIR = Path(__file__).parent
TRACE_PATH = BASE_DIR / "traces" / "ejemplo_flujo_delegacion.json"

# Techo de pasos del grafo: evita el "Supervisor Infinito" (ademas del
# criterio de suficiencia estricto dentro del propio nodo Supervisor).
RECURSION_LIMIT = 15

PREGUNTA = (
    "Investiga en la base de conocimiento los tiempos de respuesta "
    "comprometidos por severidad de soporte, y calculame el promedio en "
    "horas."
)


def _message_to_dict(message) -> dict:
    return {
        "tipo": message.__class__.__name__,
        "autor": getattr(message, "name", None),
        "contenido": message.content,
    }


async def main() -> None:
    app = compile_graph()

    print(f"=== Pregunta del usuario ===\n{PREGUNTA}\n")
    resultado = await app.ainvoke(
        {
            "messages": [HumanMessage(content=PREGUNTA)],
            "next_agent": None,
            "task_completed": False,
            "contribuciones": [],
        },
        config={"recursion_limit": RECURSION_LIMIT},
    )

    print("\n=== Respuesta final (sintesis del Supervisor) ===")
    print(resultado["messages"][-1].content)

    print("\n=== Contribuciones registradas (quien aporto que) ===")
    for c in resultado["contribuciones"]:
        print(f"  [{c['agente']}] {c['resumen'][:200]}")

    traza = {
        "pregunta": PREGUNTA,
        "mensajes": [_message_to_dict(m) for m in resultado["messages"]],
        "contribuciones": resultado["contribuciones"],
        "task_completed": resultado["task_completed"],
    }
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text(json.dumps(traza, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Traza guardada en %s", TRACE_PATH)


if __name__ == "__main__":
    asyncio.run(main())
