"""Free and free-trial hosted providers with OpenAI-compatible APIs."""

from app.ai.providers.base import ModelInfo
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


def _model(provider: str, model_id: str, name: str, context: int, *caps: str) -> ModelInfo:
    return ModelInfo(provider=provider, model_id=model_id, display_name=name,
                     context_length=context, cost_per_1k_input=0.0,
                     cost_per_1k_output=0.0, capabilities=["chat", *caps])


def free_tier_providers() -> list[OpenAICompatibleProvider]:
    """Providers whose account-level free quota can be accessed with one key."""
    return [
        OpenAICompatibleProvider(name="cerebras", base_url="https://api.cerebras.ai/v1",
            api_key=lambda: settings.CEREBRAS_API_KEY, models=[
                _model("cerebras", "gpt-oss-120b", "GPT-OSS 120B · Cerebras", 8192, "fast", "tools"),
                _model("cerebras", "llama3.1-8b", "Llama 3.1 8B · Cerebras", 8192, "fast", "tools"),
                _model("cerebras", "qwen-3-235b-a22b-instruct-2507", "Qwen 3 235B · Cerebras", 8192, "tools"),
            ]),
        OpenAICompatibleProvider(name="sambanova", base_url="https://api.sambanova.ai/v1",
            api_key=lambda: settings.SAMBANOVA_API_KEY, models=[
                _model("sambanova", "Meta-Llama-3.3-70B-Instruct", "Llama 3.3 70B · SambaNova", 131072, "fast", "tools"),
                _model("sambanova", "gpt-oss-120b", "GPT-OSS 120B · SambaNova", 131072, "reasoning", "tools"),
            ]),
        OpenAICompatibleProvider(name="huggingface", base_url="https://router.huggingface.co/v1",
            api_key=lambda: settings.HUGGINGFACE_API_KEY, models=[
                _model("huggingface", "openai/gpt-oss-120b:fastest", "GPT-OSS 120B · Hugging Face", 131072, "reasoning", "tools"),
                _model("huggingface", "deepseek-ai/DeepSeek-R1:fastest", "DeepSeek R1 · Hugging Face", 131072, "reasoning"),
            ]),
        OpenAICompatibleProvider(name="mistral", base_url="https://api.mistral.ai/v1",
            api_key=lambda: settings.MISTRAL_API_KEY, models=[
                _model("mistral", "mistral-small-latest", "Mistral Small · Free mode", 32768, "fast", "tools"),
            ]),
        OpenAICompatibleProvider(name="cohere", base_url="https://api.cohere.ai/compatibility/v1",
            api_key=lambda: settings.COHERE_API_KEY, system_role="developer", models=[
                _model("cohere", "command-a-plus-05-2026", "Command A+ · Cohere Trial", 256000, "tools"),
            ]),
        OpenAICompatibleProvider(name="nvidia", base_url="https://integrate.api.nvidia.com/v1",
            api_key=lambda: settings.NVIDIA_API_KEY, models=[
                _model("nvidia", "meta/llama-3.1-8b-instruct", "Llama 3.1 8B · NVIDIA NIM", 131072, "fast", "tools"),
            ]),
    ]
