"""Abstract contract that every provider-specific LLM client must implement."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from .schemas import ChatMessage, ModelResponse


class BaseLLMClient(ABC):
    """Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real detras."""

    @abstractmethod
    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        """Genera una respuesta completa (modo normal, no streaming)."""
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """Genera la respuesta token a token (modo streaming)."""
        raise NotImplementedError
        yield  # nunca se ejecuta; le indica a Python que este metodo es un generador
