"""Componente B - Fase 3: Estrategias de chunking y preprocesamiento.

Resuelve el ejercicio de la catedra: limpieza de texto + fragmentacion con
RecursiveCharacterTextSplitter midiendo longitud por TOKENS (no caracteres),
usando tiktoken.
"""

import logging
import re
from typing import List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("document_processor")


class DocumentProcessor:
    """Limpia y fragmenta texto en chunks acotados por cantidad de tokens."""

    def __init__(self, model_encoding: str = "cl100k_base", chunk_size: int = 500, chunk_overlap: int = 50):
        # cl100k_base es el encoding usado por modelos estilo GPT-4/GPT-3.5;
        # se usa como aproximacion estandar aunque el LLM de generacion real
        # del proyecto sea Groq/Gemini (no hay tokenizer publico exacto para
        # esos modelos, y cl100k_base es la referencia mas cercana y comun).
        self.tokenizer = tiktoken.get_encoding(model_encoding)

        # length_function mide por TOKENS, no por caracteres: asi el
        # chunk_size refleja lo que realmente le importa al LLM (su
        # ventana de contexto se mide en tokens).
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.calculate_tokens,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def clean_text(self, text: str) -> str:
        """Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios."""
        # Colapsa cualquier corrida de espacios en blanco (incluidos saltos
        # de linea multiples) a un solo espacio.
        text = re.sub(r"\s+", " ", text)
        # Normaliza puntuacion repetida (ej. "..." o ". . ." de copy-paste
        # descuidado) a un solo punto.
        text = re.sub(r"(\.\s*){2,}", ". ", text)
        return text.strip()

    def calculate_tokens(self, text: str) -> int:
        """Calcula la cantidad de tokens usando el tokenizer de tiktoken."""
        return len(self.tokenizer.encode(text))

    def process_document(self, raw_text: str) -> List[str]:
        """Pipeline: limpieza -> fragmentacion. Basura entra, basura sale:
        nunca fragmentar texto sin limpiar antes."""
        cleaned = self.clean_text(raw_text)
        chunks = self.splitter.split_text(cleaned)
        for i, chunk in enumerate(chunks):
            logger.info("Chunk %d: %d tokens", i, self.calculate_tokens(chunk))
        return chunks


if __name__ == "__main__":
    sample_text = """
    Los  microservicios   son un estilo de arquitectura de software.


    Cada servicio se despliega de forma independiente...   Esto permite
    escalar componentes por separado. . . . El uso de contenedores como
    Docker facilita el despliegue reproducible en distintos entornos.
    Kubernetes orquesta el ciclo de vida de esos contenedores en produccion.
    """

    processor = DocumentProcessor()
    chunks = processor.process_document(sample_text)
    print(f"Chunks generados: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i} ({processor.calculate_tokens(chunk)} tokens) ---")
        print(chunk)
