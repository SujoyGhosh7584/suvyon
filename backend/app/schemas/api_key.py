from typing import Literal

from pydantic import Field

from app.schemas.base import BaseSchema

ApiKeyProvider = Literal[
    "groq", "openrouter", "gemini", "cerebras", "sambanova",
    "huggingface", "mistral", "cohere", "nvidia",
]


class ApiKeyUpsert(BaseSchema):
    api_key: str = Field(min_length=8, max_length=512)


class ApiKeyStatus(BaseSchema):
    provider: ApiKeyProvider
    configured: bool
    hint: str | None = None
