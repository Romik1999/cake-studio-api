# Этап 6. Доработки и оптимизация

## Цель
Сделать проект production-ready.

## Пагинация

- [ ] Все списки через `PaginatedResponse`
- [ ] Валидация `page >= 1`, `1 <= limit <= 100`

## Фильтры

- [ ] `GET /orders?status=&delivery_date_from=&delivery_date_to=`
- [ ] `GET /ingredients?category=&is_active=`
- [ ] `GET /presets?is_active=`
- [ ] `GET /cake-configs?created_from=&created_to=`

## Сортировка

- [ ] Query-параметр `sort_by` и `order` (`asc`/`desc`)
- [ ] Белый список полей для сортировки (защита от SQL-инъекций)

## Валидация

- [ ] Обработка `IntegrityError` при DELETE → 409 Conflict
- [ ] Обработка дубликатов при POST → 400 Bad Request
- [ ] Проверка, что пользователь не может удалить чужой заказ

## Настройки в БД

- [ ] Таблица `settings` — лимит кастомных ингредиентов
- [ ] Админ может менять через API

## Тесты

- [ ] `pytest`, `httpx`, `pytest-asyncio`
- [ ] Тесты на CRUD для каждой сущности
- [ ] Тесты на авторизацию
- [ ] Тесты на расчёт цены

## Логирование

- [ ] Логировать действия админа (кто менял статус, кто удалял)
- [ ] Middleware для `X-Request-ID`
- [ ] Структурированные логи (JSON)

## Кеширование (если будет нагрузка)

- [ ] Redis для `ingredients`, `presets`
- [ ] Инвалидация при обновлении

## Безопасность

- [ ] HTTPS (на прод)
- [ ] Rate limiting (slowapi)
- [ ] CORS — только нужные origins
- [ ] Валидация всех входных данных

## Документация

- [ ] Обновить README (эндпоинты, примеры)
- [ ] Примеры curl-запросов
- [ ] Схема БД (ER-диаграмма)

## Деплой

- [ ] Prod-конфиг для Docker
- [ ] CI/CD (GitHub Actions)
- [ ] Бэкапы БД
- [ ] Мониторинг (Sentry, Prometheus)