"""Mini-script de prueba del sistema RAG local (Fase 3, Componente D).

Corre la ingesta (idempotente) y despues dos pruebas obligatorias:
- una pregunta cuya respuesta esta en los documentos,
- una pregunta trampa cuya respuesta NO esta (el sistema no debe alucinar).
"""

import asyncio
import json

from .ingest import ingest
from .rag_chain import get_rag_response

PREGUNTA_VALIDA = "Que base de datos usa el sistema de pedidos para persistencia?"
PREGUNTA_TRAMPA = "Cual es la politica de reembolsos para clientes VIP en compras internacionales?"


async def main() -> None:
    manager = ingest()

    print("=== Pregunta valida (deberia responderse desde el contexto) ===")
    resultado = await get_rag_response(PREGUNTA_VALIDA, manager)
    print(json.dumps(resultado.model_dump(), indent=2, ensure_ascii=False))

    print("\n=== Pregunta trampa (no deberia estar en el contexto) ===")
    resultado_trampa = await get_rag_response(PREGUNTA_TRAMPA, manager)
    print(json.dumps(resultado_trampa.model_dump(), indent=2, ensure_ascii=False))

    if not resultado_trampa.encontrado_en_contexto:
        print("\nOK: el sistema reconocio que la pregunta trampa no esta en el contexto.")
    else:
        print("\nADVERTENCIA: el sistema pudo haber alucinado en la pregunta trampa.")


if __name__ == "__main__":
    asyncio.run(main())
