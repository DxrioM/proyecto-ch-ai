"""Mini-script de prueba del Pipeline de Extraccion de Entidades Tecnicas.

Ejecuta process_text() con un texto tipico (descripcion de arquitectura) y
con un texto ambiguo (prueba de estres), para verificar que el pipeline
siempre devuelve un resultado valido o falla de forma controlada.
"""

import asyncio
import json

from .chain import process_text

TEXTO_EJEMPLO = (
    "El backend expone una API con FastAPI. Usamos Redis como cache de "
    "sesiones y PostgreSQL para persistencia. Bajo carga concurrente alta "
    "detectamos un cuello de botella en el pool de conexiones a la base de "
    "datos, lo que degrada el tiempo de respuesta de forma notoria."
)

# Texto deliberadamente ambiguo: no nombra ninguna tecnologia especifica ni
# describe una falla clara, para ver si el modelo se recupera (infiriendo
# igual una respuesta valida contra el esquema) o si la cadena falla de
# forma controlada despues de los reintentos.
TEXTO_AMBIGUO = "El sistema anduvo raro ayer, capaz que fue cosa de red."


async def main() -> None:
    print("=== Caso normal ===")
    resultado = await process_text(TEXTO_EJEMPLO)
    if resultado:
        print(json.dumps(resultado.model_dump(), indent=2, ensure_ascii=False))
    else:
        print("El pipeline no pudo procesar el texto (ver logs).")

    print("\n=== Prueba de estres (texto ambiguo) ===")
    resultado_ambiguo = await process_text(TEXTO_AMBIGUO)
    if resultado_ambiguo:
        print("El modelo se recupero e igual devolvio una extraccion valida:")
        print(json.dumps(resultado_ambiguo.model_dump(), indent=2, ensure_ascii=False))
    else:
        print("La cadena fallo de forma controlada (sin crashear el programa).")


if __name__ == "__main__":
    asyncio.run(main())
