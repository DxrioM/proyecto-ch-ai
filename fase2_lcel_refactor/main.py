"""Componente A - Fase 2: Refactorizacion a LCEL Asincrono.

Reemplaza la llamada manual al SDK del Modulo 1 (AsyncLLMManager propio) por
una cadena declarativa de LangChain: prompt | model | parser, ejecutada de
forma asincrona con ainvoke.

Proveedor usado: Groq (gratis, sin tarjeta), igual que en el Modulo 1.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

SYSTEM_PROMPT = (
    "Sos un asistente tecnico que responde preguntas de forma breve y clara, "
    "en espanol, sin tildes ni la letra ene con virgulilla."
)


def build_chain():
    """Compone prompt | model | parser usando el operador LCEL."""
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Falta GROQ_API_KEY en .env")

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.7,
        api_key=groq_api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{pregunta}"),
        ]
    )

    return prompt | model | StrOutputParser()


async def main() -> None:
    chain = build_chain()

    # La cadena se ejecuta de forma asincrona con ainvoke; el resultado ya es
    # texto plano (StrOutputParser extrae el .content del AIMessage).
    respuesta = await chain.ainvoke({"pregunta": "Que es la entropia? Responde en 2 lineas."})
    print("Respuesta (LCEL asincrono):")
    print(respuesta)


if __name__ == "__main__":
    asyncio.run(main())
