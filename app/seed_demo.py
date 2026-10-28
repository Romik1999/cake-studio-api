import asyncio
import random
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.security import get_password_hash
from app.database import async_session_maker
from app.models import (
    User,
    Ingredient,
    CategoryEnum,
    UnitEnum,
    Preset,
    PresetIngredient,
    CakeConfig,
    CakeIngredient,
    Order,
    StatusEnum,
    OrderStatusLog,
)


async def seed_demo():
    async with async_session_maker() as session:
        # Проверка: если данные уже есть, не дублируем
        existing = await session.execute(select(User).limit(1))
        if existing.scalar_one_or_none():
            print("⚠️ В базе уже есть пользователи. Очистите БД перед запуском сида.")
            print("Команда для очистки: docker-compose down -v && docker-compose up -d --build")
            return

        print("🚀 Начинаем наполнение базы демо-данными...")

        # ==================== 1. ПОЛЬЗОВАТЕЛИ ====================
        admin = User(
            name="Елена (Админ)",
            phone="79990000000",
            password_hash=get_password_hash("admin123"),
            is_admin=True,
        )
        clients = [
            User(name="Анна", phone="79991111111", password_hash=get_password_hash("123456")),
            User(name="Дмитрий", phone="79992222222", password_hash=get_password_hash("123456")),
            User(name="Ольга", phone="79993333333", password_hash=get_password_hash("123456")),
            User(name="Сергей", phone="79994444444", password_hash=get_password_hash("123456")),
        ]
        session.add(admin)
        session.add_all(clients)
        await session.flush()
        print("✅ Пользователи созданы")

        # ==================== 2. ИНГРЕДИЕНТЫ ====================
        doughs = [
            Ingredient(title="Шоколадный бисквит", category=CategoryEnum.DOUGH, unit=UnitEnum.GRAM,
                       base_price=Decimal("500.00"), sort_order=1),
            Ingredient(title="Ванильный бисквит", category=CategoryEnum.DOUGH, unit=UnitEnum.GRAM,
                       base_price=Decimal("450.00"), sort_order=2),
            Ingredient(title="Красный бархат", category=CategoryEnum.DOUGH, unit=UnitEnum.GRAM,
                       base_price=Decimal("600.00"), sort_order=3),
        ]
        fillings = [
            Ingredient(title="Клубничный конфи", category=CategoryEnum.FILLING, unit=UnitEnum.GRAM,
                       base_price=Decimal("200.00"), sort_order=1),
            Ingredient(title="Вишня", category=CategoryEnum.FILLING, unit=UnitEnum.GRAM, base_price=Decimal("250.00"),
                       sort_order=2),
            Ingredient(title="Карамель", category=CategoryEnum.FILLING, unit=UnitEnum.GRAM,
                       base_price=Decimal("180.00"), sort_order=3),
            Ingredient(title="Малина", category=CategoryEnum.FILLING, unit=UnitEnum.GRAM, base_price=Decimal("220.00"),
                       sort_order=4),
        ]
        creams = [
            Ingredient(title="Творожно-сливочный", category=CategoryEnum.CREAM, unit=UnitEnum.GRAM,
                       base_price=Decimal("150.00"), sort_order=1),
            Ingredient(title="Шоколадный ганаш", category=CategoryEnum.CREAM, unit=UnitEnum.GRAM,
                       base_price=Decimal("180.00"), sort_order=2),
            Ingredient(title="Маскарпоне", category=CategoryEnum.CREAM, unit=UnitEnum.GRAM,
                       base_price=Decimal("200.00"), sort_order=3),
        ]
        decorations = [
            Ingredient(title="Свежие ягоды", category=CategoryEnum.DECORATION, unit=UnitEnum.PIECE,
                       base_price=Decimal("100.00"), sort_order=1),
            Ingredient(title="Золотые шарики", category=CategoryEnum.DECORATION, unit=UnitEnum.PIECE,
                       base_price=Decimal("80.00"), sort_order=2),
        ]

        all_ingredients = doughs + fillings + creams + decorations
        session.add_all(all_ingredients)
        await session.flush()
        print("✅ Ингредиенты созданы")

        # ==================== 3. ПРЕСЕТЫ ====================
        preset1 = Preset(title="Бенто с клубникой", description="Нежный ванильный бисквит с клубникой",
                         price=Decimal("1200.00"), sort_order=1)
        preset2 = Preset(title="Шоколадный трюфель", description="Насыщенный шоколадный вкус", price=Decimal("1500.00"),
                         sort_order=2)
        preset3 = Preset(title="Красный бархат", description="Классика с маскарпоне", price=Decimal("1800.00"),
                         sort_order=3)
        session.add_all([preset1, preset2, preset3])
        await session.flush()

        preset_ingredients = [
            # Бенто с клубникой
            PresetIngredient(preset_id=preset1.id, ingredient_id=doughs[1].id, quantity="150g"),
            PresetIngredient(preset_id=preset1.id, ingredient_id=fillings[0].id, quantity="100g"),
            PresetIngredient(preset_id=preset1.id, ingredient_id=creams[0].id, quantity="100g"),
            # Шоколадный трюфель
            PresetIngredient(preset_id=preset2.id, ingredient_id=doughs[0].id, quantity="150g"),
            PresetIngredient(preset_id=preset2.id, ingredient_id=fillings[2].id, quantity="80g"),
            PresetIngredient(preset_id=preset2.id, ingredient_id=creams[1].id, quantity="120g"),
            PresetIngredient(preset_id=preset2.id, ingredient_id=decorations[1].id, quantity="5 шт"),
            # Красный бархат
            PresetIngredient(preset_id=preset3.id, ingredient_id=doughs[2].id, quantity="150g"),
            PresetIngredient(preset_id=preset3.id, ingredient_id=creams[2].id, quantity="120g"),
            PresetIngredient(preset_id=preset3.id, ingredient_id=decorations[0].id, quantity="50g"),
        ]
        session.add_all(preset_ingredients)
        await session.flush()
        print("✅ Пресеты созданы")

        # ==================== 4. КОНФИГУРАЦИИ ТОРТОВ ====================
        # Пресеты
        config1 = CakeConfig(preset_id=preset1.id, base_price=preset1.price, total_price=preset1.price)
        config2 = CakeConfig(preset_id=preset2.id, base_price=preset2.price, total_price=preset2.price)

        # Кастом
        config3 = CakeConfig(dough_id=doughs[0].id, base_price=Decimal("800.00"), total_price=Decimal("800.00"))
        config4 = CakeConfig(dough_id=doughs[2].id, base_price=Decimal("900.00"), total_price=Decimal("900.00"))

        session.add_all([config1, config2, config3, config4])
        await session.flush()

        cake_ingredients = [
            # Кастом 3
            CakeIngredient(cake_config_id=config3.id, ingredient_id=fillings[1].id, quantity="100g",
                           added_price=fillings[1].base_price),
            CakeIngredient(cake_config_id=config3.id, ingredient_id=creams[0].id, quantity="100g",
                           added_price=creams[0].base_price),
            # Кастом 4
            CakeIngredient(cake_config_id=config4.id, ingredient_id=fillings[2].id, quantity="100g",
                           added_price=fillings[2].base_price),
            CakeIngredient(cake_config_id=config4.id, ingredient_id=creams[2].id, quantity="100g",
                           added_price=creams[2].base_price),
        ]
        session.add_all(cake_ingredients)
        await session.flush()
        print("✅ Конфигурации тортов созданы")

        # ==================== 5. ЗАКАЗЫ ====================
        configs = [config1, config2, config3, config4]

        # Генерируем 25 заказов за последние 14 дней
        for i in range(25):
            user = random.choice(clients)
            config = random.choice(configs)

            days_ago = random.randint(0, 14)
            delivery_date = (datetime.now() - timedelta(days=days_ago)).date()
            delivery_time = time(hour=random.randint(10, 20), minute=0)

            # Статусы: 60% delivered, 20% preparing/paid, 10% new, 10% cancelled
            status_choice = random.choices(
                [StatusEnum.DELIVERED, StatusEnum.PAID, StatusEnum.PREPARING, StatusEnum.NEW, StatusEnum.CANCELLED],
                weights=[0.6, 0.1, 0.1, 0.1, 0.1]
            )[0]

            order = Order(
                user_id=user.id,
                cake_config_id=config.id,
                status=status_choice,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                delivery_address="ул. Ленина, д. 10",
                comment="Позвонить за час до доставки" if random.random() > 0.5 else None,
                total_price=config.total_price,
                paid_at=datetime.utcnow() - timedelta(days=days_ago) if status_choice != StatusEnum.NEW else None
            )
            session.add(order)
            await session.flush()

            # Логи
            log_new = OrderStatusLog(order_id=order.id, status=StatusEnum.NEW)
            session.add(log_new)

            if status_choice == StatusEnum.DELIVERED:
                log_del = OrderStatusLog(order_id=order.id, status=StatusEnum.DELIVERED, changed_by=admin.id)
                session.add(log_del)
            elif status_choice == StatusEnum.CANCELLED:
                log_can = OrderStatusLog(order_id=order.id, status=StatusEnum.CANCELLED, changed_by=admin.id,
                                         comment="Клиент передумал")
                session.add(log_can)

        await session.commit()
        print("✅ Заказы и логи созданы")
        print("🎉 Демо-данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(seed_demo())