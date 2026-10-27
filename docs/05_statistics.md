# Этап 5. Админка: Статистика и аналитика

## Цель
Отчёты для владельца кафе: продажи, топ-ингредиентов, частые клиенты, отмены.

## Схемы `app/schemas/statistics.py`

- [ ] `DailySalesItem` — `date`, `orders_count`, `total_revenue`
- [ ] `DailySalesResponse` — `items: list[DailySalesItem]`, `total_revenue`, `total_orders`
- [ ] `PopularIngredientItem` — `ingredient_id`, `title`, `usage_count`
- [ ] `RevenueResponse` — `total_revenue`, `avg_order_value`, `orders_count`
- [ ] `FrequentCustomerItem` — `user_id`, `name`, `phone`, `orders_count`, `total_spent`
- [ ] `CancelledOrdersResponse` — `total_cancelled`, `orders: list[OrderResponse]`
- [ ] Импорты в `app/schemas/__init__.py`

## Сервис `app/services/statistics_service.py`

- [ ] `get_daily_sales(session, start_date, end_date)`:
  - Группировка по `delivery_date`
  - Только `DELIVERED` заказы
- [ ] `get_popular_ingredients(session, limit=10)`:
  - Объединить `cake_ingredients` + `preset_ingredients`
  - `GROUP BY ingredient_id ORDER BY COUNT DESC`
- [ ] `get_revenue(session, start_date, end_date)`:
  - `SUM(total_price)` по `DELIVERED`
  - Средний чек
- [ ] `get_frequent_customers(session, limit=10)`:
  - `GROUP BY user_id ORDER BY COUNT(orders) DESC`
- [ ] `get_cancelled_orders(session, page, limit)`:
  - Список заказов со статусом `CANCELLED`

## Эндпоинты `app/api/v1/admin/statistics.py`

- [ ] `GET /admin/statistics/daily?start_date=&end_date=`
- [ ] `GET /admin/statistics/popular-ingredients?limit=10`
- [ ] `GET /admin/statistics/revenue?start_date=&end_date=`
- [ ] `GET /admin/statistics/frequent-customers?limit=10`
- [ ] `GET /admin/statistics/cancelled?page=&limit=`

## Защита
- [ ] Все роуты — `Depends(get_current_admin)`
- [ ] Роутер монтируется с префиксом `/admin`

## Проверка
- Создать 5–10 заказов с разными датами
- Проверить каждый отчёт через Swagger