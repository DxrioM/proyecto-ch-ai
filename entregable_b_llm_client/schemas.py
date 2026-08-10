"""Pydantic schemas shared across every LLM client and the manager."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, field_validator

ALLOWED_ROLES = {"user", "assistant", "system"}


class Provider(str, Enum):
    """Supported LLM providers behind the unified interface."""

    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"


class ChatMessage(BaseModel):
    """A single message in a conversation."""

    role: str = Field(description="'user', 'assistant' o 'system'")
    content: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ALLOWED_ROLES:
            raise ValueError(f"role debe ser uno de {ALLOWED_ROLES}, recibido: '{v}'")
        return v


class LLMConfig(BaseModel):
    """Configuration required to instantiate a provider client via the factory."""

    provider: Provider
    model: str
    openai_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None
    groq_api_key: Optional[SecretStr] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)


class ModelResponse(BaseModel):
    """Uniform response returned by every client, success or failure."""

    provider: Provider
    model: str
    content: str
    error: Optional[str] = None
