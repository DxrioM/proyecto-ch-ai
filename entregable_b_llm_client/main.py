"""Script de validacion del Unified Async LLM Client.

Carga las variables de entorno, crea un AsyncLLMManager por proveedor
configurado y hace una pregunta corta tanto en modo normal como en
streaming. Incluye ademas una prueba de resiliencia: OpenAI se prueba
a proposito sin key valida para demostrar que el error queda contenido
en ModelResponse.error y el programa sigue vivo.
"""

import asyncio
import os

from dotenv import load_dotenv
from pydantic import SecretStr

from .llm_manager import AsyncLLMManager
from .schemas import ChatMessage, LLMConfig, Provider

PREGUNTA = [ChatMessage(role="user", content="Que es el cambrico? Responde en 2 lineas.")]


async def probar_proveedor(nombre_visible: str, config: LLMConfig) -> None:
    print(f"\n=== {nombre_visible} ===")
    try:
        manager = AsyncLLMManager(config)
    except ValueError as e:
        print(f"No se pudo crear el cliente: {e}")
        return

    print("-- Modo normal --")
    resultado = await manager.generate(PREGUNTA)
    if resultado.error:
        print(f"Error controlado (el programa sigue vivo): {resultado.error}")
    else:
        print(resultado.content)

    print("-- Modo streaming --")
    async for chunk in manager.generate_stream(PREGUNTA):
        print(chunk, end="", flush=True)
    print()


async def main() -> None:
    load_dotenv()

    google_api_key = os.environ.get("GOOGLE_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if google_api_key:
        await probar_proveedor(
            "Gemini",
            LLMConfig(
                provider=Provider.GEMINI,
                model="gemini-flash-latest",
                google_api_key=SecretStr(google_api_key),
                temperature=0.7,
                # gemini-flash-latest reserva parte de max_tokens para "thinking"
                # interno antes de la respuesta visible; con 200 la respuesta
                # queda cortada a mitad de frase.
                max_tokens=500,
            ),
        )
    else:
        print("\n=== Gemini === omitido: falta GOOGLE_API_KEY en .env")

    if groq_api_key:
        await probar_proveedor(
            "Groq",
            LLMConfig(
                provider=Provider.GROQ,
                model="llama-3.3-70b-versatile",
                groq_api_key=SecretStr(groq_api_key),
                temperature=0.7,
                max_tokens=200,
            ),
        )
    else:
        print("\n=== Groq === omitido: falta GROQ_API_KEY en .env")

    # Prueba de resiliencia deliberada: sin key (o key invalida) de OpenAI.
    # Objetivo: demostrar que un proveedor sin credenciales validas devuelve
    # el error dentro de ModelResponse (o como chunk de streaming) en vez de
    # tirar abajo el script.
    await probar_proveedor(
        "OpenAI (prueba de resiliencia: key ausente o invalida a proposito)",
        LLMConfig(
            provider=Provider.OPENAI,
            model="gpt-4o-mini",
            openai_api_key=SecretStr(openai_api_key or "sk-key-invalida-a-proposito"),
            temperature=0.7,
            max_tokens=200,
        ),
    )

    print("\nEl programa termino sin crashear pese a los errores anteriores.")


if __name__ == "__main__":
    asyncio.run(main())
