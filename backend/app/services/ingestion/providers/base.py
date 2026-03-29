"""Abstract base for LLM providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    provider: str
    model: str


class LLMProvider(ABC):
    """Synchronous LLM provider interface.

    Implementations are synchronous; callers should use asyncio.to_thread
    when calling from async contexts.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def complete(self, system: str, user: str) -> LLMResponse:
        """Send a single-turn prompt and return the response."""
