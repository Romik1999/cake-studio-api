# Этап 2. Авторизация и пользователи

## Цель
JWT-авторизация, регистрация клиентов, роли (админ/клиент).

## Зависимости
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

## Core

- [ ] `app/core/security.py`:
  - `get_password_hash(password: str) -> str`
  - `verify_password(plain, hashed) -> bool`
  - `create_access_token(data: dict, expires_delta: timedelta) -> str`
  - `decode_token(token: str) -> dict`

## Схемы `app/schemas/user.py`

- [ ] `UserBase` — `name`, `phone`, `email`
- [ ] `UserCreate(UserBase)` — + `password`
- [ ] `UserResponse(UserBase)` — + `id`, `is_admin`, `created_at`, `from_attributes=True`
- [ ] `UserLogin` — `phone`, `password`
- [ ] `TokenResponse` — `access_token`, `token_type`
- [ ] Импорты в `app/schemas/__init__.py`

## Сервис `app/services/user_service.py`

- [ ] `get_by_phone(session, phone) -> User | None`
- [ ] `get_by_id(session, user_id) -> User | None`
- [ ] `create(session, data) -> User` — с хешированием пароля
- [ ] `authenticate(session, phone, password) -> User | None`

## DI-зависимости `app/api/deps.py`

- [ ] `get_current_user()`:
  - Читает `Authorization: Bearer <token>`
  - Декодирует JWT
  - Находит пользователя в БД
  - Возвращает `User` или 401
- [ ] `get_current_admin()`:
  - Вызывает `get_current_user`
  - Проверяет `is_admin`
  - Иначе 403

## Эндпоинты `app/api/v1/auth.py`

- [ ] `POST /auth/register` — регистрация клиента → `UserResponse`
- [ ] `POST /auth/login` — выдать JWT → `TokenResponse`
- [ ] `GET /auth/me` — текущий пользователь → `UserResponse`

## Защита админских роутов

- [ ] `POST /ingredients` — `Depends(get_current_admin)`
- [ ] `PATCH /ingredients/{id}` — `Depends(get_current_admin)`
- [ ] `DELETE /ingredients/{id}` — `Depends(get_current_admin)`
- [ ] То же для `presets`

## Подключение
- [ ] `app/api/v1/__init__.py` — добавить `auth_router`

## Проверка
- Регистрация → логин → получить JWT → `/auth/me` с токеном
- Без токена → 401 на защищённых роутах
- С токеном клиента → 403 на админских роутах