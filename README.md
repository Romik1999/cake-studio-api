# Cake Studio API 🍰

Backend-приложение для кондитерской: конструктор тортов на заказ + админка с аналитикой.

## Стек

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy (async)** — ORM
- **Alembic** — миграции
- **Pydantic v2** — валидация данных
- **Docker / Docker Compose** — контейнеризация

## Структура проекта

```
cake-studio-api/
├── app/
│   ├── api/v1/           # Роуты (версия 1)
│   ├── models/           # SQLAlchemy-модели
│   ├── schemas/          # Pydantic-схемы
│   ├── services/         # Бизнес-логика
│   ├── config.py         # Настройки
│   ├── database.py       # Подключение к БД
│   ├── seed.py           # Создание суперадмина
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

SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🐳 Запуск через Docker

### Первый запуск

```bash
# Собрать образы и поднять контейнеры
docker-compose up -d --build

# Применить миграции
docker-compose exec api alembic upgrade head

# Создать суперадмина (сид)
docker-compose exec api python -m app.seed
```

Приложение доступно: http://localhost:8000  
Swagger: http://localhost:8000/docs

### Ежедневная работа

```bash
# Поднять контейнеры
docker-compose up -d

# Посмотреть логи
docker-compose logs -f api

# Остановить
docker-compose down

# Остановить + удалить данные БД
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

# Создать БД
createdb cake-studio-api

# Применить миграции
alembic upgrade head

# Создать суперадмина
python -m app.seed
```

### Ежедневная работа

```bash
# Активировать venv
source .venv/bin/activate

# Запустить сервер разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение доступно: http://localhost:8000  
Swagger: http://localhost:8000/docs

### Миграции

```bash
alembic revision --autogenerate -m "описание"
alembic upgrade head
alembic downgrade -1
```

---

## Полезные команды

```bash
# Зайти в контейнер
docker-compose exec api sh

# Подключиться к PostgreSQL (в контейнере)
docker-compose exec db psql -U postgres -d cake-studio-api

# Посмотреть список таблиц
docker-compose exec db psql -U postgres -d cake-studio-api -c "\dt"

# Проверить структуру таблицы
docker-compose exec db psql -U postgres -d cake-studio-api -c "\d ingredients"

# Текущая версия миграций
docker-compose exec api alembic current
```

---

## Функциональность (план)

- [x] Модели БД (User, Ingredient, Preset, CakeConfig, Order)
- [x] CRUD для ингредиентов
- [ ] CRUD для пресетов
- [ ] Авторизация (JWT)
- [ ] Конструктор тортов
- [ ] Заказы и статусы
- [ ] Статистика для админа

## Лицензия

MIT