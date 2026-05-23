import json

import pytest
import respx
from httpx import Response

from cba.llm.client import (
    LlmInvalidResponseError,
    LlmMessage,
    LlmProvider,
    LlmProviderError,
    LlmRequest,
    LlmRole,
)
from cba.llm.ollama import OllamaLlmClient


@pytest.mark.anyio
@respx.mock
async def test_ollama_generate_success() -> None:
    client = OllamaLlmClient(base_url="http://mock-ollama:11434", model="test-model")
    
    mock_response = {
        "model": "test-model",
        "created_at": "2023-08-04T08:52:19.385406455Z",
        "message": {"role": "assistant", "content": "Hello! How can I help you?"},
        "done": True,
        "total_duration": 512345678,
        "load_duration": 123456,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 456789,
        "eval_count": 20,
        "eval_duration": 987654,
    }
    
    respx.post("http://mock-ollama:11434/api/chat").mock(
        return_value=Response(200, json=mock_response)
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Hi")],
        model="test-model",
        provider=LlmProvider.OLLAMA,
    )

    response = await client.generate(request)

    assert response.text == "Hello! How can I help you?"
    assert response.model == "test-model"
    assert response.provider == LlmProvider.OLLAMA
    assert response.usage["prompt_tokens"] == 10
    assert response.usage["completion_tokens"] == 20
    assert response.usage["total_tokens"] == 30
    assert response.metadata["total_duration"] == 512345678


@pytest.mark.anyio
@respx.mock
async def test_ollama_generate_json_success() -> None:
    client = OllamaLlmClient(base_url="http://mock-ollama:11434")
    
    content_json = {"answer": "Paris", "confidence": 0.99}
    mock_response = {
        "model": "qwen2.5:3b",
        "message": {"role": "assistant", "content": json.dumps(content_json)},
        "done": True,
    }
    
    respx.post("http://mock-ollama:11434/api/chat").mock(
        return_value=Response(200, json=mock_response)
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Capital of France?")],
        model="qwen2.5:3b",
        provider=LlmProvider.OLLAMA,
        response_schema_name="capital_info"
    )

    response = await client.generate(request)

    assert response.parsed_json == content_json
    assert response.text == json.dumps(content_json)


@pytest.mark.anyio
@respx.mock
async def test_ollama_generate_invalid_json_raises_error() -> None:
    client = OllamaLlmClient()
    
    mock_response = {
        "model": "qwen2.5:3b",
        "message": {"role": "assistant", "content": "This is not JSON"},
        "done": True,
    }
    
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=Response(200, json=mock_response)
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Give me JSON")],
        model="qwen2.5:3b",
        provider=LlmProvider.OLLAMA,
        response_schema_name="some_schema"
    )

    with pytest.raises(LlmInvalidResponseError, match="Failed to parse expected JSON"):
        await client.generate(request)


@pytest.mark.anyio
@respx.mock
async def test_ollama_http_error_mapping() -> None:
    client = OllamaLlmClient()
    
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=Response(404, text="Model not found")
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Hi")],
        model="non-existent-model",
        provider=LlmProvider.OLLAMA,
    )

    with pytest.raises(LlmProviderError, match="Ollama API returned error: 404"):
        await client.generate(request)


@pytest.mark.anyio
@respx.mock
async def test_ollama_missing_content_error() -> None:
    client = OllamaLlmClient()
    
    # Missing 'content' inside 'message'
    mock_response = {
        "model": "qwen2.5:3b",
        "message": {"role": "assistant"},
        "done": True,
    }
    
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=Response(200, json=mock_response)
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Hi")],
        model="qwen2.5:3b",
        provider=LlmProvider.OLLAMA,
    )

    with pytest.raises(LlmProviderError, match="Unexpected Ollama response shape"):
        await client.generate(request)


@pytest.mark.anyio
@respx.mock
async def test_ollama_connection_error_mapping() -> None:
    client = OllamaLlmClient(base_url="http://invalid-host")
    
    # Use httpx.ConnectError for a more realistic connection failure
    import httpx
    respx.post("http://invalid-host/api/chat").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Hi")],
        model="qwen2.5:3b",
        provider=LlmProvider.OLLAMA,
    )

    with pytest.raises(LlmProviderError, match="Failed to connect to Ollama"):
        await client.generate(request)


@pytest.mark.anyio
@respx.mock
async def test_ollama_injected_client_reuse() -> None:
    # Verify that an injected client is used and not closed
    import httpx
    async with httpx.AsyncClient() as shared_client:
        client = OllamaLlmClient(client=shared_client)
        
        mock_response = {
            "model": "qwen2.5:3b",
            "message": {"role": "assistant", "content": "Reuse test"},
            "done": True,
        }
        respx.post("http://localhost:11434/api/chat").mock(
            return_value=Response(200, json=mock_response)
        )

        request = LlmRequest(
            messages=[LlmMessage(role=LlmRole.USER, content="Hi")],
            model="qwen2.5:3b",
            provider=LlmProvider.OLLAMA,
        )

        resp = await client.generate(request)
        assert resp.text == "Reuse test"
        
        # Injected client should still be open
        assert not shared_client.is_closed
