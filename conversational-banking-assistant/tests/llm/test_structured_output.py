import pytest
from pydantic import BaseModel, ConfigDict, Field, RootModel

from cba.llm.client import LlmInvalidResponseError, LlmProvider, LlmResponse
from cba.llm.structured_output import StructuredOutputValidator


class LlmTestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    decision: str
    answer: str
    citations: list[str] = Field(default_factory=list)


def test_validate_raw_json() -> None:
    raw_text = '{"decision": "Yes", "answer": "Paris", "citations": ["C1"]}'
    result = StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    
    assert result.decision == "Yes"
    assert result.answer == "Paris"
    assert result.citations == ["C1"]


def test_validate_fenced_json_with_lang() -> None:
    raw_text = """
Here is the result:
```json
{
  "decision": "No",
  "answer": "London",
  "citations": []
}
```
Hope that helps!
    """.strip()
    result = StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    assert result.decision == "No"
    assert result.answer == "London"


def test_validate_fenced_json_without_lang() -> None:
    raw_text = "```\n{\"decision\": \"Yes\", \"answer\": \"Berlin\", \"citations\": []}\n```"
    result = StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    assert result.decision == "Yes"
    assert result.answer == "Berlin"


def test_validate_response_prefers_parsed_json() -> None:
    # Text is invalid, but parsed_json is valid
    response = LlmResponse(
        text="Invalid JSON",
        parsed_json={"decision": "Yes", "answer": "Madrid", "citations": []},
        model="test",
        provider=LlmProvider.FAKE
    )
    result = StructuredOutputValidator.validate_response(response, LlmTestResponse)
    assert result.answer == "Madrid"


def test_validate_invalid_json_fails() -> None:
    raw_text = '{"decision": "Yes", "answer": "broken' # Missing quote and brace
    with pytest.raises(LlmInvalidResponseError) as excinfo:
        StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    
    assert "Failed to decode JSON" in str(excinfo.value)
    assert excinfo.value.schema_name == "LlmTestResponse"
    assert excinfo.value.raw_text == raw_text


def test_validate_missing_field_fails() -> None:
    raw_text = '{"decision": "Yes"}' # Missing 'answer'
    with pytest.raises(LlmInvalidResponseError) as excinfo:
        StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    
    assert "Validation failed" in str(excinfo.value)
    assert any("answer" in err for err in excinfo.value.errors or [])


def test_validate_extra_field_fails_with_forbid() -> None:
    raw_text = '{"decision": "Yes", "answer": "X", "extra": "hallucination"}'
    with pytest.raises(LlmInvalidResponseError) as excinfo:
        StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    
    assert "extra" in str(excinfo.value.errors)


def test_validate_type_mismatch_fails() -> None:
    raw_text = '{"decision": "Yes", "answer": 123, "citations": "not-a-list"}'
    with pytest.raises(LlmInvalidResponseError) as excinfo:
        StructuredOutputValidator.validate(raw_text, LlmTestResponse)
    
    assert any("answer" in err for err in excinfo.value.errors or [])
    assert any("citations" in err for err in excinfo.value.errors or [])


def test_validate_empty_string_fails() -> None:
    with pytest.raises(LlmInvalidResponseError, match="empty response"):
        StructuredOutputValidator.validate("  ", LlmTestResponse)


def test_error_message_truncation() -> None:
    huge_text = "{" + "A" * 1000
    with pytest.raises(LlmInvalidResponseError) as excinfo:
        StructuredOutputValidator.validate(huge_text, LlmTestResponse)
    
    assert len(excinfo.value.raw_text or "") <= 105 # 100 + "..."


def test_validate_list_root_schema() -> None:
    class Item(BaseModel):
        id: int

    raw_text = '[{"id": 1}, {"id": 2}]'
    
    class ItemList(RootModel[list[Item]]):
        pass
        
    result = StructuredOutputValidator.validate(raw_text, ItemList)
    assert len(result.root) == 2
    assert result.root[0].id == 1
