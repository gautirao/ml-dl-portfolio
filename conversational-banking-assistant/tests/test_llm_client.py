import json
import os

import pytest
from pydantic import ValidationError

from cba.llm.client import (
    LlmMessage,
    LlmProvider,
    LlmProviderError,
    LlmRequest,
    LlmResponse,
    LlmRole,
)
from cba.llm.fake import FakeLlmClient


def test_llm_request_validation() -> None:
    # Valid request
    request = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="Hello")],
        model="test-model",
        provider=LlmProvider.FAKE,
    )
    assert request.model == "test-model"
    assert request.provider == "fake"

    # Missing required field
    with pytest.raises(ValidationError):
        LlmRequest(model="test-model", provider=LlmProvider.FAKE)  # type: ignore


def test_llm_response_serialization() -> None:
    response = LlmResponse(
        text='{"answer": "yes"}',
        parsed_json={"answer": "yes"},
        model="test-model",
        provider=LlmProvider.FAKE,
        usage={"tokens": 10},
        metadata={"latency": 100},
    )

    data = response.model_dump()
    assert data["text"] == '{"answer": "yes"}'
    assert data["parsed_json"] == {"answer": "yes"}
    assert data["usage"] == {"tokens": 10}

    # Round trip
    new_response = LlmResponse(**data)
    assert new_response == response


@pytest.mark.anyio
async def test_fake_llm_client_queued_responses() -> None:
    client = FakeLlmClient()

    res1 = LlmResponse(text="First", model="m1", provider=LlmProvider.FAKE)
    res2 = LlmResponse(text="Second", model="m1", provider=LlmProvider.FAKE)

    client.add_response(res1)
    client.add_response(res2)

    req = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="hi")],
        model="m1",
        provider=LlmProvider.FAKE,
    )

    out1 = await client.generate(req)
    assert out1.text == "First"

    out2 = await client.generate(req)
    assert out2.text == "Second"

    # Default fallback
    out3 = await client.generate(req)
    assert out3.text == "Default fake response"


@pytest.mark.anyio
async def test_fake_llm_client_parsed_json() -> None:
    client = FakeLlmClient()

    parsed_data = {"status": "ok", "evidence_found": True}
    res = LlmResponse(
        text=json.dumps(parsed_data),
        parsed_json=parsed_data,
        model="m1",
        provider=LlmProvider.FAKE,
    )
    client.add_response(res)

    req = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="hi")],
        model="m1",
        provider=LlmProvider.FAKE,
    )

    out = await client.generate(req)
    assert out.parsed_json == parsed_data


@pytest.mark.anyio
async def test_fake_llm_client_invalid_json() -> None:
    client = FakeLlmClient()

    # We can simulate an invalid JSON response by providing text that isn't JSON
    # but setting parsed_json to None.
    res = LlmResponse(
        text="This is not JSON",
        parsed_json=None,
        model="m1",
        provider=LlmProvider.FAKE,
    )
    client.add_response(res)

    req = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="hi")],
        model="m1",
        provider=LlmProvider.FAKE,
    )

    out = await client.generate(req)
    assert out.text == "This is not JSON"
    assert out.parsed_json is None


@pytest.mark.anyio
async def test_fake_llm_client_provider_error() -> None:
    client = FakeLlmClient()
    client.add_error(LlmProviderError("Connection failed"))

    req = LlmRequest(
        messages=[LlmMessage(role=LlmRole.USER, content="hi")],
        model="m1",
        provider=LlmProvider.FAKE,
    )

    with pytest.raises(LlmProviderError, match="Connection failed"):
        await client.generate(req)


def test_retrieval_does_not_import_llm() -> None:
    """
    Check that core retrieval modules do not import cba.llm to maintain boundary.
    """
    retrieval_dir = os.path.join("src", "cba", "retrieval")
    for root, _, files in os.walk(retrieval_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                    assert "from cba.llm" not in content
                    assert "import cba.llm" not in content
