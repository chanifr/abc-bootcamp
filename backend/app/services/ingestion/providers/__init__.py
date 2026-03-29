"""LLM provider factory."""
from app.services.ingestion.providers.base import LLMProvider, LLMResponse


def build_provider(
    provider_name: str,
    model: str,
    region: str = "us-east-1",
    aws_access_key_id: str = "",
    aws_secret_access_key: str = "",
    aws_bearer_token: str = "",
    anthropic_api_key: str = "",
) -> LLMProvider:
    """Instantiate the requested provider.  Raises ValueError on unknown name."""
    if provider_name == "bedrock":
        from app.services.ingestion.providers.bedrock import BedrockProvider

        return BedrockProvider(
            model=model,
            region=region,
            aws_access_key_id=aws_access_key_id or None,
            aws_secret_access_key=aws_secret_access_key or None,
            bearer_token=aws_bearer_token or None,
        )
    elif provider_name == "anthropic":
        from app.services.ingestion.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=anthropic_api_key, model=model)
    else:
        raise ValueError(
            f"Unknown INGESTION_PROVIDER {provider_name!r}. Choose 'bedrock' or 'anthropic'."
        )


__all__ = ["LLMProvider", "LLMResponse", "build_provider"]