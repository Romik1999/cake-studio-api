# Этап 1. Модели, миграции, CRUD справочников

## Цель
Создать все таблицы БД, Pydantic-схемы, CRUD для `Ingredient` и `Preset`.

## Модели

- [x] `app/models/user.py` — `User`
- [x] `app/models/ingredient.py` — `Ingredient` + `CategoryEnum`, `UnitEnum`
- [x] `app/models/preset.py` — `Preset`
- [x] `app/models/preset_ingredient.py` — `PresetIngredient`
- [x] `app/models/cake_config.py` — `CakeConfig`
- [x] `app/models/cake_ingredient.py` — `CakeIngredient`
- [x] `app/models/order.py` — `Order` + `StatusEnum`
- [x] `app/models/order_status_log.py` — `OrderStatusLog`
- [x] Импорты в `app/models/__init__.py`

## Миграция
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Схемы

- [x] `app/schemas/ingredient.py` — Create/Update/Response
- [x] `app/schemas/preset.py` — Create/Update/Response/Detail + PresetIngredientCreate/Detail
- [x] `app/schemas/response.py` — `SuccessResponse[T]`
- [x] `app/schemas/pagination.py` — `PaginatedResponse[T]`, `PaginationMeta`
- [x] Импорты в `app/schemas/__init__.py`

## Сервисы

- [x] `app/services/ingredient_service.py`:
  - `get_all()` → `(items, total)`
  - `get_by_id()`
  - `create()` — `flush` + `refresh`
  - `update()` — `exclude_unset=True`
  - `delete()`
- [x] `app/services/preset_service.py`:
  - `get_all()` → `(items, total)`
  - `get_by_id()` — с `selectinload` в 2 уровня
  - `create()` — с созданием `PresetIngredient`
  - `update()` — с пересборкой состава
  - `delete()`

## Эндпоинты

- [x] `app/api/v1/ingredients.py` — 5 роутов
- [x] `app/api/v1/presets.py` — 5 роутов
- [x] `app/api/v1/__init__.py` — `api_router`
- [x] `main.py` → `app.include_router(api_router, prefix="/api/v1")`

## Правила проекта

- **Коммит — в эндпоинте**, `flush` — в сервисе
- **Сессия** — через `Depends(get_session)`
- **Сервис** возвращает ORM-объект
- **HTTPException** — только в эндпоинте
- **PATCH** для обновлений (не PUT)
- Обёртка ответа — `{success, data}` или `{success, data, meta}`

## Проверка
- Swagger `/docs` → все роуты доступны
- Создать ингредиент → получить список → обновить → удалить