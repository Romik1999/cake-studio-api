# Этап 0. Настройка проекта

## Цель
Развернуть FastAPI + PostgreSQL + Alembic + Docker.

## Задачи

- [x] Создать структуру папок:
  ```
  app/
  ├── api/v1/
  ├── core/
  ├── models/
  ├── schemas/
  ├── services/
  ```
- [x] `requirements.txt`:
  ```
  fastapi
  uvicorn
  sqlalchemy
  alembic
  asyncpg
  greenlet
  python-dotenv
  pydantic-settings
  passlib[bcrypt]
  python-jose[cryptography]
  ```
- [x] `app/config.py` — `Settings` + `get_settings()` с `lru_cache`
- [x] `app/database.py`:
  - `create_async_engine`
  - `async_session_maker`
  - `Base`
  - `get_session()` — async generator для `Depends`
- [x] Alembic:
  - `alembic init -t async migrations`
  - Настроить `migrations/env.py` (async)
  - Убрать `sqlalchemy.url` из `alembic.ini`, брать из `settings.DATABASE_URL`
- [x] `.env` и `.env.example`
- [x] `Dockerfile` и `docker-compose.yml`
- [x] `main.py` с CORS + `/health` + lifespan
- [x] `README.md`
- [x] `.dockerignore`, `.gitignore`

## Проверка
- `docker-compose up -d`
- `curl http://localhost:8000/health` → 200
- `http://localhost:8000/docs` открывается