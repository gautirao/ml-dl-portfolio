import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .client import LlmInvalidResponseError, LlmResponse

T = TypeVar("T", bound=BaseModel)


class StructuredOutputValidator:
    """
    Validator for structured JSON output from LLMs.
    Extracts JSON from text (including markdown fences) and validates against a Pydantic model.
    """

    @staticmethod
    def extract_json(text: str) -> str:
        """
        Extract JSON from text. 
        Supports raw JSON, markdown fenced JSON (with or without 'json' language identifier).
        """
        text = text.strip()
        
        # 1. Try markdown fenced code blocks first
        # Pattern matches ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()
            
        # 2. Fallback: try to find the first '{' or '[' and the last '}' or ']'
        # This is a basic attempt to find a JSON object/array within prose.
        # We only do this if it looks like there might be something there.
        match = re.search(r"([\[{].*[\]}])", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        return text

    @classmethod
    def validate(cls, text: str, target_model: type[T]) -> T:
        """
        Extract and validate JSON string against a Pydantic model.
        """
        if not text.strip():
            raise LlmInvalidResponseError(
                message="LLM returned an empty response",
                schema_name=target_model.__name__,
                raw_text="",
            )

        json_str = cls.extract_json(text)
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Truncate raw text for the error message
            snippet = (text[:100] + "...") if len(text) > 100 else text
            raise LlmInvalidResponseError(
                message=f"Failed to decode JSON: {e}",
                schema_name=target_model.__name__,
                raw_text=snippet,
            ) from e

        return cls.validate_data(data, target_model, raw_text=text)

    @classmethod
    def validate_data(
        cls, 
        data: Any, 
        target_model: type[T], 
        raw_text: str | None = None
    ) -> T:
        """
        Validate a dictionary/list against a Pydantic model.
        """
        try:
            return target_model.model_validate(data)
        except ValidationError as e:
            snippet = ""
            if raw_text:
                snippet = (raw_text[:100] + "...") if len(raw_text) > 100 else raw_text
                
            errors = [str(err) for err in e.errors()]
            raise LlmInvalidResponseError(
                message=f"Validation failed for schema '{target_model.__name__}'",
                schema_name=target_model.__name__,
                raw_text=snippet,
                errors=errors,
            ) from e

    @classmethod
    def validate_response(cls, response: LlmResponse, target_model: type[T]) -> T:
        """
        Validate an LlmResponse against a Pydantic model.
        Prefers response.parsed_json if available.
        """
        if response.parsed_json is not None:
            return cls.validate_data(
                response.parsed_json, 
                target_model, 
                raw_text=response.text
            )
        
        return cls.validate(response.text, target_model)
