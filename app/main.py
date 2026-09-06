import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

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
app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI"),
    version=os.getenv("APP_VERSION", "v1"),
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
