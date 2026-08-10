"""AsyncLLMManager: punto de entrada unico y agnostico al proveedor (patron Factory)."""

from typing import AsyncGenerator, List

from .base_client import BaseLLMClient
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .openai_client import OpenAIClient
from .schemas import ChatMessage, LLMConfig, ModelResponse, Provider


class AsyncLLMManager:
    """Recibe un LLMConfig, arma internamente el cliente concreto y delega en el."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: BaseLLMClient = self._build_client()

    def _build_client(self) -> BaseLLMClient:
        if self.config.provider == Provider.OPENAI:
            if not self.config.openai_api_key:
                raise ValueError("Falta openai_api_key en la configuracion")
            return OpenAIClient(
                api_key=self.config.openai_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        if self.config.provider == Provider.GEMINI:
            if not self.config.google_api_key:
                raise ValueError("Falta google_api_key en la configuracion")
            return GeminiClient(
                api_key=self.config.google_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        if self.config.provider == Provider.GROQ:
            if not self.config.groq_api_key:
                raise ValueError("Falta groq_api_key en la configuracion")
            return GroqClient(
                api_key=self.config.groq_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        raise ValueError(f"Proveedor no soportado: {self.config.provider}")

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        return await self._client.generate(messages)

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        async for chunk in self._client.generate_stream(messages):
            yield chunk
