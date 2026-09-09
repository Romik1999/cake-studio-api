import os
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()

# Создаем асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Включаем логирование SQL (для разработки)
    pool_size=5,  # Оптимально для старта
    max_overflow=10
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Базовый класс для моделей
Base = declarative_base()

# Вспомогательная функция для получения сессии (для dependency injection)
async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_maker() as session:
        yield session