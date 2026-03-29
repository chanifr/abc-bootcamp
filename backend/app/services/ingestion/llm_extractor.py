"""LLM extraction stage.

Calls the configured provider and returns the raw LLM response.
JSON parsing and validation happen downstream in validator.py.
"""
import asyncio
import json

from app.services.ingestion.providers.base import LLMProvider, LLMResponse
from app.services.ingestion.prompts import cv_extraction_v1, job_extraction_v1


class LLMExtractionError(Exception):
    """Raised when the LLM call itself fails (network, auth, etc.)."""


def _choose_prompt_module(document_type: str):
    if document_type == "cv":
        return cv_extraction_v1
    elif document_type == "job_description":
        return job_extraction_v1
    else:
        raise ValueError(f"Unknown document_type: {document_type!r}")


def extract_sync(
    raw_text: str, document_type: str, provider: LLMProvider
) -> tuple[str, str, str, LLMResponse]:
    """Run LLM extraction synchronously.

    Returns (system_prompt, user_prompt, prompt_version, llm_response).
    Raises LLMExtractionError on provider failure.
    """
    prompt_module = _choose_prompt_module(document_type)
    system, user, version = prompt_module.build_prompt(raw_text)

    try:
        response = provider.complete(system=system, user=user)
    except Exception as exc:
        raise LLMExtractionError(str(exc)) from exc

    return system, user, version, response


async def extract_async(
    raw_text: str, document_type: str, provider: LLMProvider
) -> tuple[str, str, str, LLMResponse]:
    """Async wrapper — runs the synchronous provider in a thread pool."""
    return await asyncio.to_thread(extract_sync, raw_text, document_type, provider)


def strip_json_fences(text: str) -> str:
    """Remove markdown code fences that some models add despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        # Strip opening fence (```json or ```)
        text = text[text.index("\n") + 1:] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    return text.strip()


def parse_llm_json(raw_output: str) -> dict:
    """Parse LLM output as JSON.  Raises ValueError with context on failure."""
    cleaned = strip_json_fences(raw_output)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM output is not valid JSON: {exc}\n\nRaw output (first 500 chars):\n"
            f"{raw_output[:500]}"
        ) from exc
