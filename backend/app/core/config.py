from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.

    All configuration values must come from environment variables
    or the .env file. Never hardcode secrets anywhere else.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
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
    DEBUG: bool = False

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

    SUPABASE_URL: str

    SUPABASE_KEY: str

    # --------------------------------------------------
    # AI Providers
    # --------------------------------------------------

    OPENROUTER_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

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


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()
