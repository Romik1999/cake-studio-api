# Cake Studio API 🍰

Backend-приложение для кондитерской: конструктор тортов на заказ + админка с аналитикой.

**Мультитенантность:** Одна база данных, изоляция данных по `tenant_id` на уровне БД (Shared Schema + Composite Foreign Keys).

## Стек

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy (async)** — ORM
- **Alembic** — миграции
- **Pydantic v2 + pydantic-settings** — валидация данных и конфиг
- **JWT (python-jose)** — авторизация и роли (CUSTOMER, ADMIN, SUPERADMIN)
- **Docker / Docker Compose** — контейнеризация
- **Ruff** — линтер и форматтер

## Структура проекта

```text
cake-studio-api/
├── app/
│   ├── api/
│   │   ├── deps.py       # Зависимости (get_current_user, get_tenant_admin, get_superadmin)
│   │   └── v1/           # Роуты (версия 1)
│   │       ├── admin/    # Статистика (только для админов тенанта)
│   │       ├── superadmin/ # Управление тенантами (только для суперадмина)
│   │       ├── auth.py
│   │       ├── cake_configs.py
│   │       ├── ingredients.py
│   │       ├── orders.py
│   │       └── presets.py
│   ├── core/             # Безопасность (JWT, хеширование, шифрование)
│   ├── models/           # SQLAlchemy-модели (с tenant_id и composite FK)
│   ├── schemas/          # Pydantic-схемы
│   ├── services/         # Бизнес-логика (изоляция по tenant_id)
│   ├── config.py         # Настройки (BaseSettings)
│   ├── database.py       # Подключение к БД
│   ├── seed.py           # Заполнение БД демо-данными
│   └── main.py           # Точка входа
├── docs/                 # Документация (Postman collection)
├── migrations/           # Alembic-миграции
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Переменные окружения (`.env`)

```env
ENV=local

APP_NAME=cake-studio-api
APP_VERSION=1.0.0

# Для Docker
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/cake-studio-api

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cake-studio-api

SECRET_KEY=change-me-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ключ для шифрования (Fernet)
# Сгенерировать: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-fernet-key-here

# CORS (для фронта)
CORS_ORIGINS=["http://localhost:5173"]
CORS_ORIGIN_REGEX=https://([a-z0-9-]+\.)?cake-studio\.ru

# Тенант по умолчанию для локальной разработки
TENANT_DEFAULT_SLUG=moments
```

---

## 🐳 Запуск через Docker (Рекомендуется)

### Первый запуск

```bash
# Собрать образы и поднять контейнеры (с healthcheck для БД)
docker-compose up -d --build

# Применить миграции (создать таблицы, enum-типы, composite FK)
docker-compose run --rm api alembic upgrade head

# Заполнить БД тестовыми данными (3 тенанта, ингредиенты, пресеты, заказы)
docker-compose run --rm api python -m app.seed
```

Приложение доступно: http://localhost:8000  
Swagger (Документация): http://localhost:8000/docs

> **Данные для входа после сида (пароль у всех `admin123`):**
> - **Суперадмин (Платформа):** `+79000000000` (Header: `X-Tenant: platform`)
> - **Админ "Моменты сладости":** `+79001111111` (Header: `X-Tenant: moments`)
> - **Админ "Тестовой пекарни":** `+79002222222` (Header: `X-Tenant: bakery2`)

> ⚠️ **ВАЖНО:** При тестировании через `localhost` (Swagger или Postman) **обязательно** передавайте заголовок `X-Tenant` со слагом нужной кондитерской. Без него бэкенд не поймет, к какой базе применять запрос. В продакшене тенант будет определяться автоматически по поддомену (например, `moments.cake-studio.ru`).

### Ежедневная работа

```bash
# Поднять контейнеры
docker-compose up -d

# Посмотреть логи
docker-compose logs -f api

# Остановить
docker-compose down

# Остановить + удалить данные БД (полный сброс)
docker-compose down -v

# Пересобрать после изменения requirements.txt
docker-compose up -d --build
```

### Миграции

```bash
# Создать новую миграцию
docker-compose run --rm api alembic revision --autogenerate -m "описание"

# Применить
docker-compose run --rm api alembic upgrade head

# Откатить последнюю
docker-compose run --rm api alembic downgrade -1
```

---

## 💻 Запуск локально (без Docker)

### Первый запуск

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Установить зависимости (включая Ruff)
pip install -r requirements.txt

# Убедиться, что PostgreSQL запущен локально (например, через brew)
brew services start postgresql
createdb cake-studio-api

# Применить миграции
alembic upgrade head

# Заполнить БД демо-данными
python -m app.seed
```

### Ежедневная работа

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🛣 Основные эндпоинты (API v1)

Все эндпоинты имеют префикс `/api/v1`.

**Авторизация (требуют заголовок `X-Tenant`):**
- `POST /auth/register` — Регистрация клиента (автоматически привязывается к текущему тенанту)
- `POST /auth/login` — Получение JWT-токена (возвращает `tenant_slug` и `role`)
- `GET /auth/me` — Профиль текущего пользователя

**Конструктор и справочники:**
- `GET /ingredients` — Список ингредиентов тенанта (с фильтрами)
- `POST/PATCH/DELETE /ingredients` — Управление (только `ADMIN` тенанта)
- `GET /presets` — Список готовых пресетов тенанта
- `POST/PATCH/DELETE /presets` — Управление (только `ADMIN` тенанта)
- `POST /cake-configs` — Собрать кастомный торт (автоматический расчёт цены, проверка чужих ингредиентов)
- `GET /cake-configs` — Список конфигураций тенанта

**Заказы:**
- `POST /orders` — Создать заказ (клиент создается автоматически по телефону)
- `GET /orders` — Список заказов (админ видит все заказы тенанта, клиент — только свои)
- `GET /orders/{id}` — Детали заказа
- `PATCH /orders/{id}/status` — Сменить статус (только `ADMIN` тенанта)
- `PATCH /orders/{id}/cancel` — Отменить заказ

**Аналитика (только для админа тенанта):**
- `GET /admin/statistics/daily` — Продажи по дням
- `GET /admin/statistics/popular-ingredients` — Топ популярных начинок
- `GET /admin/statistics/revenue` — Общая выручка и средний чек
- `GET /admin/statistics/frequent-customers` — Частые клиенты
- `GET /admin/statistics/cancelled` — Список отмененных заказов

**Управление платформой (только для `SUPERADMIN`):**
- `GET /superadmin/tenants` — Список всех кондитерских на платформе

---

## 🧪 Тестирование (Swagger)

1. Откройте `http://localhost:8000/docs`.
2. Нажмите кнопку **Authorize** (замочек в правом верхнем углу).
3. В поле `X-Tenant` введите слаг кондитерской (например, `moments`).
4. Авторизуйтесь через `POST /auth/login` (используйте телефон и пароль админа из сида).
5. Скопируйте `access_token` и вставьте его в поле `Bearer` в окне **Authorize**.
6. Теперь вам доступны защищенные ручки. Если вы попытаетесь сделать запрос с токеном `moments` к `X-Tenant: bakery2`, сервер вернет `401 Unauthorized`.

---

## Функциональность (Статус MVP)

- [x] Мультитенантность (изоляция на уровне Composite FK в БД)
- [x] Модели БД и миграции (User, Ingredient, Preset, CakeConfig, Order, StatusLog, Tenant)
- [x] CRUD для ингредиентов и пресетов (в рамках тенанта)
- [x] Ролевая модель (`CUSTOMER`, `ADMIN`, `SUPERADMIN`) и JWT
- [x] Конструктор тортов с динамическим расчётом цены (защита от чужих ингредиентов)
- [x] Оформление заказов и трекинг статусов
- [x] Панель аналитики для владельца (строго по своему тенанту)
- [x] Изолированные Telegram-уведомления для каждого тенанта
- [x] Скрипт демо-данных (3 тенанта)

## Лицензия

MIT