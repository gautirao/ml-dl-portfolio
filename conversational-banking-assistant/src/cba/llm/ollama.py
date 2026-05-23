import json
import os
from typing import Any

import httpx

from .client import (
    LlmClient,
    LlmInvalidResponseError,
    LlmProvider,
    LlmProviderError,
    LlmRequest,
    LlmResponse,
)


class OllamaLlmClient(LlmClient):
    """
    LLM client implementation using Ollama's local REST API.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """
        Initialize the Ollama client.
        Prioritizes: constructor args > environment variables > defaults.
        """
        self.base_url = (
            base_url or os.getenv("CBA_OLLAMA_BASE_URL") or "http://localhost:11434"
        ).rstrip("/")
        self.default_model = model or os.getenv("CBA_OLLAMA_MODEL") or "qwen2.5:3b"
        self.timeout = (
            timeout_seconds
            or float(os.getenv("CBA_OLLAMA_TIMEOUT_SECONDS") or "60.0")
        )
        self._client = client

    async def generate(self, request: LlmRequest) -> LlmResponse:
        """
        Generate a response using Ollama's /api/chat endpoint.
        """
        url = f"{self.base_url}/api/chat"

        # Mapping LlmRequest to Ollama chat payload
        payload = {
            "model": request.model or self.default_model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }

        # If a schema name is provided, hint at JSON format
        if request.response_schema_name:
            payload["format"] = "json"

        try:
            if self._client:
                response = await self._client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
        except httpx.HTTPStatusError as e:
            msg = f"Ollama API returned error: {e.response.status_code} - {e.response.text}"
            raise LlmProviderError(msg) from e
        except httpx.RequestError as e:
            raise LlmProviderError(f"Failed to connect to Ollama: {e}") from e
        except json.JSONDecodeError as e:
            raise LlmProviderError(f"Failed to parse Ollama response as JSON: {e}") from e

        # Response shape validation
        if "message" not in data or "content" not in data["message"]:
            raise LlmProviderError(
                f"Unexpected Ollama response shape: missing 'message.content'. Raw: {data}"
            )

        content = data["message"]["content"]
        parsed_json: dict[str, Any] | None = None

        # JSON parsing logic
        if request.response_schema_name:
            try:
                parsed_json = json.loads(content)
            except json.JSONDecodeError as e:
                msg = (
                    f"Failed to parse expected JSON response for schema "
                    f"'{request.response_schema_name}': {e}"
                )
                raise LlmInvalidResponseError(msg) from e
        else:
            # Optional: attempt to parse JSON if it looks like it, but don't fail if it isn't
            if content.strip().startswith(("{", "[")):
                try:
                    parsed_json = json.loads(content)
                except json.JSONDecodeError:
                    parsed_json = None

        return LlmResponse(
            text=content,
            parsed_json=parsed_json,
            model=data.get("model", request.model or self.default_model),
            provider=LlmProvider.OLLAMA,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            metadata={
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "prompt_eval_duration": data.get("prompt_eval_duration"),
                "eval_duration": data.get("eval_duration"),
            },
        )
