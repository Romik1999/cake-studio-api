# Этап 3. Конструктор торта

## Цель
Пользователь собирает торт (кастом или пресет), бэкенд считает цену.

## Схемы `app/schemas/cake_config.py`

- [ ] `CakeIngredientCreate` — `ingredient_id`, `quantity`, `added_price?`, `sort_order?`
- [ ] `CakeIngredientDetail` — + `ingredient: IngredientResponse`
- [ ] `DecorationSchema` — `type`, `text?`, `color?`, `position?`
- [ ] `CakeConfigCreate`:
  - `dough_id: int | None`
  - `preset_id: int | None`
  - `cake_ingredients: list[CakeIngredientCreate]`
  - `decoration: DecorationSchema | None`
- [ ] `CakeConfigUpdate` — всё опционально
- [ ] `CakeConfigResponse` — базовые поля + `base_price`, `total_price`
- [ ] `CakeConfigDetail(CakeConfigResponse)` — + `dough`, `preset`, `cake_ingredients`
- [ ] Импорты в `app/schemas/__init__.py`

## Сервис `app/services/cake_config_service.py`

- [ ] `get_all(session, page, limit) -> (items, total)`
- [ ] `get_by_id(session, id)` — с `selectinload` в 3 уровня:
  ```
  cake_ingredients.ingredient, dough, preset
  ```
- [ ] `_calculate_price(session, dough_id, preset_id, cake_ingredients) -> (base, total)`:
  - Если `preset_id` — берем `preset.price`
  - Если кастом — `dough.base_price + сумма(base_price ингредиентов)`
- [ ] `create(session, data) -> CakeConfig`:
  - Проверка: либо `preset_id`, либо `dough_id`
  - Лимит кастомных ингредиентов (пока хардкод 5)
  - Создать `CakeConfig` → `flush` → создать `CakeIngredient` → `flush`
  - Перезапросить с `selectinload`
- [ ] `update(session, id, data)` — аналогично
- [ ] `delete(session, id) -> bool`

## Эндпоинты `app/api/v1/cake_configs.py`

- [ ] `GET /cake-configs` — пагинация
- [ ] `GET /cake-configs/{id}` — с составом
- [ ] `POST /cake-configs` — создать
- [ ] `PATCH /cake-configs/{id}` — обновить
- [ ] `DELETE /cake-configs/{id}` — удалить

## Бизнес-правила

- Если `preset_id` передан → `dough_id` и `cake_ingredients` игнорируются
- Если `preset_id` не передан → `dough_id` обязателен
- Максимум кастомных ингредиентов — 5 (пока)
- `total_price` фиксируется на момент создания

## Проверка
- Создать кастом (корж + 3 начинки) → цена посчитана
- Создать через пресет → цена = пресет.price
- `GET /cake-configs/{id}` → всё вернулось с вложенными объектами