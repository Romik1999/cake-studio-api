import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "cake-studio-api")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cake_craft")

@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (с кэшированием)"""
    return Settings()