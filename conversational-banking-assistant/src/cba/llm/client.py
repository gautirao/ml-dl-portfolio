from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LlmProvider(StrEnum):
    FAKE = "fake"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class LlmRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LlmMessage(BaseModel):
    role: LlmRole
    content: str


class LlmRequest(BaseModel):
    messages: list[LlmMessage]
    model: str
    provider: LlmProvider
    temperature: float = 0.0
    max_tokens: int = 1024
    response_schema_name: str | None = None


class LlmResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    text: str
    parsed_json: dict[str, Any] | None = None
    model: str
    provider: LlmProvider
    usage: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LlmError(Exception):
    """Base exception for LLM-related issues."""
    pass


class LlmInvalidResponseError(LlmError):
    """Raised when the model fails to return a valid format or JSON."""
    pass


class LlmProviderError(LlmError):
    """Raised for upstream API failures, timeouts, or connection issues."""
    pass


class LlmClient(ABC):
    @abstractmethod
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate a response from the LLM."""
        pass
