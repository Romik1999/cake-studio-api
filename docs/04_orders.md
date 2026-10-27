# Этап 4. Заказы и статусы

## Цель
Оформление заказа, управление статусами, лог изменений.

## Схемы `app/schemas/order.py`

- [ ] `OrderCreate`:
  - `cake_config_id: int`
  - `user_phone: str`
  - `user_name: str`
  - `delivery_date: date`
  - `delivery_time: time`
  - `delivery_address: str | None`
  - `comment: str | None`
- [ ] `OrderResponse` — `id`, `status`, `total_price`, `delivery_date`, `delivery_time`, `created_at`
- [ ] `OrderDetail(OrderResponse)` — + `user`, `cake_config`, `status_log`
- [ ] `OrderStatusUpdate` — `status: StatusEnum`, `comment: str | None`
- [ ] `OrderStatusLogResponse`
- [ ] Импорты в `app/schemas/__init__.py`

## Сервис `app/services/order_service.py`

- [ ] `create(session, data) -> Order`:
  - Найти/создать `User` по `phone`
  - Проверить, что `cake_config` существует
  - Скопировать `total_price` из `cake_config`
  - `status = NEW`
  - `flush` → создать `OrderStatusLog` с `NEW`
  - Перезапросить с `selectinload`
- [ ] `get_all(session, filters, page, limit)` — для админа (все заказы)
- [ ] `get_user_orders(session, user_id, page, limit)` — для клиента
- [ ] `get_by_id(session, id)` — с `selectinload` (user, cake_config, status_log)
- [ ] `update_status(session, id, new_status, changed_by, comment) -> Order`:
  - Обновить `order.status`
  - Если `PAID` → проставить `paid_at`
  - Создать `OrderStatusLog`
- [ ] `cancel(session, id, changed_by) -> Order` — то же, но `CANCELLED`

## Эндпоинты `app/api/v1/orders.py`

- [ ] `POST /orders` — создать (доступно всем, без токена)
- [ ] `GET /orders` — список (админ: все; клиент: только свои)
- [ ] `GET /orders/{id}` — детали (с проверкой владельца)
- [ ] `PATCH /orders/{id}/status` — смена статуса (только админ)
- [ ] `PATCH /orders/{id}/cancel` — отмена (владелец или админ)

## Статусы
```
NEW → PAID → PREPARING → READY → DELIVERED
                            ↓
                        CANCELLED (из любого)
```

## Проверка
- Создать заказ → автоматически создался user
- Сменить статус админом → запись в `order_status_log`
- Клиент видит только свои заказы