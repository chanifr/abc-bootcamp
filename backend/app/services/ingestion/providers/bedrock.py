"""AWS Bedrock provider (default — uses Amazon Nova via Converse API)."""
import os
import time

from app.services.ingestion.providers.base import LLMProvider, LLMResponse


class BedrockProvider(LLMProvider):
    """Calls AWS Bedrock using the Converse API.

    Authentication supports two modes (in priority order):
    1. Bearer token (AWS_BEARER_TOKEN_BEDROCK) — Bedrock-native API key
    2. IAM credentials (access key + secret) — standard boto3 credential chain
    """

    def __init__(
        self,
        model: str = "amazon.nova-pro-v1:0",
        region: str = "us-east-1",
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        bearer_token: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("boto3 is not installed") from exc

        # Bearer token: set as env var so boto3 picks it up automatically
        if bearer_token:
            os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bearer_token

        kwargs: dict = {"region_name": region}
        if aws_access_key_id:
            kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            kwargs["aws_secret_access_key"] = aws_secret_access_key

        self._client = boto3.client("bedrock-runtime", **kwargs)

    @property
    def provider_name(self) -> str:
        return "bedrock"

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> LLMResponse:
        t0 = time.monotonic()
        try:
            response = self._client.converse(
                modelId=self._model,
                system=[{"text": system}],
                messages=[{"role": "user", "content": [{"text": user}]}],
                inferenceConfig={
                    "maxTokens": self._max_tokens,
                    "temperature": self._temperature,
                },
            )
        except Exception as exc:
            raise RuntimeError(f"Bedrock Converse call failed: {exc}") from exc

        latency_ms = int((time.monotonic() - t0) * 1000)
        content = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})
        return LLMResponse(
            content=content,
            input_tokens=usage.get("inputTokens", 0),
            output_tokens=usage.get("outputTokens", 0),
            latency_ms=latency_ms,
            provider="bedrock",
            model=self._model,
        )
