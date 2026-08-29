from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None  # tool name for role="tool" messages


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    tool_calls: list[dict] | None = None


@dataclass
class ModelInfo:
    provider: str
    model_id: str
    display_name: str
    context_length: int
    supports_streaming: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    capabilities: list[str] = field(default_factory=list)


class BaseLLMProvider(ABC):
    """
    Abstract interface every LLM provider must implement.
    """

    provider_name: str

    @abstractmethod
    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        """Send messages and return a complete response."""

    @abstractmethod
    def stream(
        self, messages: list[LLMMessage], model: str, **kwargs
    ) -> Iterator[str]:
        """Stream response tokens one chunk at a time."""

    @abstractmethod
    def list_models(self) -> list[ModelInfo]:
        """Return all models this provider exposes."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider is configured and reachable."""
