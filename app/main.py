import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import get_settings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт: создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Стоп: закрываем соединения
    await engine.dispose()


# Инициализация Fastapi app
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return Response(status_code=200)
