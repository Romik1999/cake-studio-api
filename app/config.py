from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    ENV: Literal["local", "staging", "prod"] = "local"

    APP_NAME: str = "cake-studio-api"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ENCRYPTION_KEY: str

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""

    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    CORS_ORIGIN_REGEX: str | None = r"https://([a-z0-9-]+\.)?cake-studio\.ru"

    TENANT_DEFAULT_SLUG: str = "moments"


@lru_cache()
def get_settings() -> Settings:
    return Settings()