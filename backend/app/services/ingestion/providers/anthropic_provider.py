"""Anthropic Claude provider (comparison option)."""
import time

from app.services.ingestion.providers.base import LLMProvider, LLMResponse

_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


class AnthropicProvider(LLMProvider):
    """Calls the Anthropic Messages API."""

    def __init__(
        self,
        api_key: str,
        model: str = _DEFAULT_MODEL,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("anthropic package is not installed") from exc

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when provider=anthropic")

        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> LLMResponse:
        t0 = time.monotonic()
        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:
            raise RuntimeError(f"Anthropic API call failed: {exc}") from exc

        latency_ms = int((time.monotonic() - t0) * 1000)
        content = message.content[0].text
        return LLMResponse(
            content=content,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            latency_ms=latency_ms,
            provider="anthropic",
            model=self._model,
        )
