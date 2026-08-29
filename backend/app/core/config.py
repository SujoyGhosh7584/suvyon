from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """
    Centralized application configuration.

    All configuration values must come from environment variables
    or the .env file. Never hardcode secrets anywhere else.
    """

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --------------------------------------------------
    # Application
    # --------------------------------------------------

    APP_NAME: str = "Suvyon"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development")

    # --------------------------------------------------
    # API
    # --------------------------------------------------

    API_V1_PREFIX: str = "/api/v1"

    # --------------------------------------------------
    # Security
    # --------------------------------------------------

    SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    DATABASE_URL: str

    # --------------------------------------------------
    # Supabase
    # --------------------------------------------------

    SUPABASE_URL: str = ""

    SUPABASE_KEY: str = ""

    # --------------------------------------------------
    # AI Providers
    # --------------------------------------------------

    OPENROUTER_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    TAVILY_API_KEY: str = ""

    SERPER_API_KEY: str = ""

    BRAVE_API_KEY: str = ""

    # --------------------------------------------------
    # Email
    # --------------------------------------------------

    SMTP_HOST: str = ""

    SMTP_PORT: int = 587

    SMTP_USERNAME: str = ""

    SMTP_PASSWORD: str = ""

    SMTP_FROM_EMAIL: str = ""

    # --------------------------------------------------
    # CORS
    # --------------------------------------------------

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                import json

                return json.loads(text)
            return [item.strip() for item in text.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()


def sqlalchemy_database_url(raw: str | None = None) -> str:
    url = (raw if raw is not None else settings.DATABASE_URL).strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url
