# Cake Studio API 🍰

Backend-приложение для кондитерской: конструктор тортов на заказ + админка с аналитикой.

## Стек

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy (async)** — ORM
- **Alembic** — миграции
- **Pydantic v2** — валидация данных
- **JWT (python-jose)** — авторизация и роли
- **Docker / Docker Compose** — контейнеризация

## Структура проекта

```text
cake-studio-api/
├── app/
│   ├── api/
│   │   ├── deps.py       # Зависимости (get_current_user, get_current_admin)
│   │   └── v1/           # Роуты (версия 1)
│   │       ├── admin/    # Роуты статистики (только для админов)
│   │       ├── auth.py
│   │       ├── cake_configs.py
│   │       ├── ingredients.py
│   │       ├── orders.py
│   │       └── presets.py
│   ├── core/             # Безопасность (хеширование, JWT)
│   ├── models/           # SQLAlchemy-модели
│   ├── schemas/          # Pydantic-схемы
│   ├── services/         # Бизнес-логика
│   ├── config.py         # Настройки
│   ├── database.py       # Подключение к БД
│   ├── seed_demo.py      # Заполнение БД демо-данными
│   └── main.py           # Точка входа
├── migrations/           # Alembic-миграции
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Переменные окружения (`.env`)

```env
APP_NAME=cake-studio-api
APP_VERSION=1.0.0

# Для Docker
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/cake-studio-api

# Для локального запуска
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cake-studio-api

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cake-studio-api

SECRET_KEY=change-me-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🐳 Запуск через Docker (Рекомендуется)

### Первый запуск

```bash
# Собрать образы и поднять контейнеры
docker-compose up -d --build

# Применить миграции (создать таблицы)
docker-compose exec api alembic upgrade head

# Заполнить БД тестовыми данными (ингредиенты, пресеты, заказы, юзеры)
docker-compose exec api python -m app.seed_demo
```

Приложение доступно: http://localhost:8000  
Swagger (Документация): http://localhost:8000/docs

> **Данные для входа в админку после сида:**
> - **Телефон:** `79990000000`
> - **Пароль:** `admin123`

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
docker-compose exec api alembic revision --autogenerate -m "описание"

# Применить
docker-compose exec api alembic upgrade head

# Откатить последнюю
docker-compose exec api alembic downgrade -1
```

---

## 💻 Запуск локально (без Docker)

### Первый запуск

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Установить зависимости
pip install -r requirements.txt

# Убедиться, что PostgreSQL запущен локально (например, через brew)
brew services start postgresql
createdb cake-studio-api

# Применить миграции
alembic upgrade head

# Заполнить БД демо-данными
python -m app.seed_demo
```

### Ежедневная работа

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🛣 Основные эндпоинты (API v1)

Все эндпоинты имеют префикс `/api/v1`.

**Авторизация:**
- `POST /auth/register` — Регистрация клиента
- `POST /auth/login` — Получение JWT-токена
- `GET /auth/me` — Профиль текущего пользователя

**Конструктор и справочники:**
- `GET /ingredients` — Список ингредиентов (с фильтрами)
- `POST/PATCH/DELETE /ingredients` — Управление (только админ)
- `GET /presets` — Список готовых пресетов
- `POST/PATCH/DELETE /presets` — Управление (только админ)
- `POST /cake-configs` — Собрать кастомный торт или выбрать пресет (автоматический расчёт цены)
- `GET /cake-configs` — Список конфигураций

**Заказы:**
- `POST /orders` — Создать заказ (публичный, клиент создается автоматически по телефону)
- `GET /orders` — Список заказов (админ видит все, клиент — только свои)
- `GET /orders/{id}` — Детали заказа
- `PATCH /orders/{id}/status` — Сменить статус (только админ)
- `PATCH /orders/{id}/cancel` — Отменить заказ

**Аналитика (только для админа):**
- `GET /admin/statistics/daily` — Продажи по дням
- `GET /admin/statistics/popular-ingredients` — Топ популярных начинок
- `GET /admin/statistics/revenue` — Общая выручка и средний чек
- `GET /admin/statistics/frequent-customers` — Частые клиенты
- `GET /admin/statistics/cancelled` — Список отмененных заказов

---

## 🧪 Тестирование (Swagger)

1. Откройте `http://localhost:8000/docs`.
2. Авторизуйтесь через `POST /auth/login` (используйте телефон и пароль админа из сида).
3. Скопируйте `access_token`.
4. Нажмите кнопку **Authorize** (замочек в правом верхнем углу) и вставьте токен.
5. Теперь вам доступны защищенные ручки (создание ингредиентов, статистика и т.д.).

---

## Функциональность (Статус MVP)

- [x] Модели БД и миграции (User, Ingredient, Preset, CakeConfig, Order, StatusLog)
- [x] CRUD для ингредиентов и пресетов
- [x] Ролевая модель и JWT-авторизация
- [x] Конструктор тортов с динамическим расчётом цены
- [x] Оформление заказов и трекинг статусов
- [x] Панель аналитики для владельца
- [x] Скрипт демо-данных для презентации

## Лицензия

MIT