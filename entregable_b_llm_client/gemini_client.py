"""Google Gemini provider client (free tier, no credit card required)."""

from typing import AsyncGenerator, List, Optional, Tuple

from google import genai
from google.genai import types

from .base_client import BaseLLMClient
from .schemas import ChatMessage, ModelResponse, Provider


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self._client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _convert_messages(
        self, messages: List[ChatMessage]
    ) -> Tuple[List[types.Content], Optional[str]]:
        """Gemini separa el system prompt del resto y llama 'model' al rol del asistente."""
        contents = []
        system_instruction = None
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                gemini_role = "model" if m.role == "assistant" else "user"
                contents.append(types.Content(role=gemini_role, parts=[types.Part(text=m.content)]))
        return contents, system_instruction

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            contents, system_instruction = self._convert_messages(messages)
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    system_instruction=system_instruction,
                ),
            )
            return ModelResponse(provider=Provider.GEMINI, model=self.model, content=response.text or "")
        except Exception as e:
            return ModelResponse(
                provider=Provider.GEMINI, model=self.model, content="",
                error=f"Error de la API de Gemini: {e}",
            )

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            contents, system_instruction = self._convert_messages(messages)
            stream = await self._client.aio.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    system_instruction=system_instruction,
                ),
            )
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[Error durante el streaming: {e}]"
