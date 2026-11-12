import asyncio
import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import get_password_hash
from app.database import async_session_maker
from app.models import (
    Tenant, User, UserRole,
    Ingredient, CategoryEnum, UnitEnum,
    Preset, PresetIngredient,
    CakeConfig, CakeIngredient,
    Order, StatusEnum, OrderStatusLog,
)


async def seed():
    async with async_session_maker() as session:
        existing = (
            await session.execute(select(Tenant).where(Tenant.slug == "platform"))
        ).scalar_one_or_none()
        if existing:
            print("⚠️  Seed already applied. Run `docker compose down -v` to reset.")
            return

        print("🚀 Seeding...")

        # ==================== 1. TENANTS ====================
        platform = Tenant(slug="platform", name="Cake Studio", domain="cake-studio.ru", is_active=True)
        moments = Tenant(slug="moments", name="Моменты сладости", domain="moments.cake-studio.ru", is_active=True)
        bakery2 = Tenant(slug="bakery2", name="Тестовая пекарня", domain="bakery2.cake-studio.ru", is_active=True)
        session.add_all([platform, moments, bakery2])
        await session.flush()
        print("✅ Tenants created")

        # ==================== 2. USERS ====================
        superadmin = User(
            name="Platform Owner",
            phone="+79000000000",
            email="owner@cake-studio.ru",
            password_hash=get_password_hash("admin123"),
            role=UserRole.SUPERADMIN,
            tenant_id=platform.id,
        )
        admin = User(
            name="Елена",
            phone="+79001111111",
            email="elena@moments.ru",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            tenant_id=moments.id,
        )
        clients = [
            User(name="Анна", phone="+79001111112", password_hash=get_password_hash("123456"), role=UserRole.CUSTOMER, tenant_id=moments.id),
            User(name="Дмитрий", phone="+79001111113", password_hash=get_password_hash("123456"), role=UserRole.CUSTOMER, tenant_id=moments.id),
            User(name="Ольга", phone="+79001111114", password_hash=get_password_hash("123456"), role=UserRole.CUSTOMER, tenant_id=moments.id),
            User(name="Сергей", phone="+79001111115", password_hash=get_password_hash("123456"), role=UserRole.CUSTOMER, tenant_id=moments.id),
        ]
        admin_bakery2 = User(
            name="Иван",
            phone="+79002222222",
            email="ivan@bakery2.ru",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            tenant_id=bakery2.id,
        )
        session.add_all([superadmin, admin, *clients, admin_bakery2])
        await session.flush()
        print("✅ Users created")

        # ==================== 3. INGREDIENTS (moments) ====================
        doughs = [
            Ingredient(tenant_id=moments.id, title="Шоколадный бисквит", category=CategoryEnum.DOUGH,
                       unit=UnitEnum.GRAM, base_price=Decimal("500.00"), sort_order=1),
            Ingredient(tenant_id=moments.id, title="Ванильный бисквит", category=CategoryEnum.DOUGH,
                       unit=UnitEnum.GRAM, base_price=Decimal("450.00"), sort_order=2),
            Ingredient(tenant_id=moments.id, title="Красный бархат", category=CategoryEnum.DOUGH,
                       unit=UnitEnum.GRAM, base_price=Decimal("600.00"), sort_order=3),
        ]
        fillings = [
            Ingredient(tenant_id=moments.id, title="Клубничный конфи", category=CategoryEnum.FILLING,
                       unit=UnitEnum.GRAM, base_price=Decimal("200.00"), sort_order=1),
            Ingredient(tenant_id=moments.id, title="Вишня", category=CategoryEnum.FILLING,
                       unit=UnitEnum.GRAM, base_price=Decimal("250.00"), sort_order=2),
            Ingredient(tenant_id=moments.id, title="Карамель", category=CategoryEnum.FILLING,
                       unit=UnitEnum.GRAM, base_price=Decimal("180.00"), sort_order=3),
            Ingredient(tenant_id=moments.id, title="Малина", category=CategoryEnum.FILLING,
                       unit=UnitEnum.GRAM, base_price=Decimal("220.00"), sort_order=4),
        ]
        creams = [
            Ingredient(tenant_id=moments.id, title="Творожно-сливочный", category=CategoryEnum.CREAM,
                       unit=UnitEnum.GRAM, base_price=Decimal("150.00"), sort_order=1),
            Ingredient(tenant_id=moments.id, title="Шоколадный ганаш", category=CategoryEnum.CREAM,
                       unit=UnitEnum.GRAM, base_price=Decimal("180.00"), sort_order=2),
            Ingredient(tenant_id=moments.id, title="Маскарпоне", category=CategoryEnum.CREAM,
                       unit=UnitEnum.GRAM, base_price=Decimal("200.00"), sort_order=3),
        ]
        decorations = [
            Ingredient(tenant_id=moments.id, title="Свежие ягоды", category=CategoryEnum.DECORATION,
                       unit=UnitEnum.PIECE, base_price=Decimal("100.00"), sort_order=1),
            Ingredient(tenant_id=moments.id, title="Золотые шарики", category=CategoryEnum.DECORATION,
                       unit=UnitEnum.PIECE, base_price=Decimal("80.00"), sort_order=2),
        ]
        session.add_all(doughs + fillings + creams + decorations)

        # bakery2 — для проверки изоляции
        bakery2_ingredients = [
            Ingredient(tenant_id=bakery2.id, title="Ванильный бисквит", category=CategoryEnum.DOUGH,
                       unit=UnitEnum.GRAM, base_price=Decimal("450.00"), sort_order=1),
            Ingredient(tenant_id=bakery2.id, title="Крем-чиз", category=CategoryEnum.CREAM,
                       unit=UnitEnum.GRAM, base_price=Decimal("170.00"), sort_order=1),
        ]
        session.add_all(bakery2_ingredients)
        await session.flush()
        print("✅ Ingredients created")

        # ==================== 4. PRESETS (moments) ====================
        preset1 = Preset(tenant_id=moments.id, title="Бенто с клубникой",
                         description="Нежный ванильный бисквит с клубникой",
                         price=Decimal("1200.00"), sort_order=1)
        preset2 = Preset(tenant_id=moments.id, title="Шоколадный трюфель",
                         description="Насыщенный шоколадный вкус",
                         price=Decimal("1500.00"), sort_order=2)
        preset3 = Preset(tenant_id=moments.id, title="Красный бархат",
                         description="Классика с маскарпоне",
                         price=Decimal("1800.00"), sort_order=3)
        session.add_all([preset1, preset2, preset3])
        await session.flush()

        session.add_all([
            PresetIngredient(tenant_id=moments.id, preset_id=preset1.id, ingredient_id=doughs[1].id, quantity="150g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset1.id, ingredient_id=fillings[0].id, quantity="100g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset1.id, ingredient_id=creams[0].id, quantity="100g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset2.id, ingredient_id=doughs[0].id, quantity="150g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset2.id, ingredient_id=fillings[2].id, quantity="80g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset2.id, ingredient_id=creams[1].id, quantity="120g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset2.id, ingredient_id=decorations[1].id, quantity="5 шт"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset3.id, ingredient_id=doughs[2].id, quantity="150g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset3.id, ingredient_id=creams[2].id, quantity="120g"),
            PresetIngredient(tenant_id=moments.id, preset_id=preset3.id, ingredient_id=decorations[0].id, quantity="50g"),
        ])
        await session.flush()
        print("✅ Presets created")

        # ==================== 5. CAKE CONFIGS (moments) ====================
        config1 = CakeConfig(tenant_id=moments.id, preset_id=preset1.id,
                             base_price=preset1.price, total_price=preset1.price)
        config2 = CakeConfig(tenant_id=moments.id, preset_id=preset2.id,
                             base_price=preset2.price, total_price=preset2.price)
        config3 = CakeConfig(tenant_id=moments.id, dough_id=doughs[0].id,
                             base_price=Decimal("800.00"), total_price=Decimal("800.00"))
        config4 = CakeConfig(tenant_id=moments.id, dough_id=doughs[2].id,
                             base_price=Decimal("900.00"), total_price=Decimal("900.00"))
        session.add_all([config1, config2, config3, config4])
        await session.flush()

        session.add_all([
            CakeIngredient(tenant_id=moments.id, cake_config_id=config3.id, ingredient_id=fillings[1].id,
                           quantity="100g", added_price=fillings[1].base_price),
            CakeIngredient(tenant_id=moments.id, cake_config_id=config3.id, ingredient_id=creams[0].id,
                           quantity="100g", added_price=creams[0].base_price),
            CakeIngredient(tenant_id=moments.id, cake_config_id=config4.id, ingredient_id=fillings[2].id,
                           quantity="100g", added_price=fillings[2].base_price),
            CakeIngredient(tenant_id=moments.id, cake_config_id=config4.id, ingredient_id=creams[2].id,
                           quantity="100g", added_price=creams[2].base_price),
        ])
        await session.flush()
        print("✅ Cake configs created")

        # ==================== 6. ORDERS (moments) ====================
        configs = [config1, config2, config3, config4]

        for _ in range(25):
            user = random.choice(clients)
            config = random.choice(configs)
            days_ago = random.randint(0, 14)
            delivery_date = (datetime.now() - timedelta(days=days_ago)).date()
            delivery_time = time(hour=random.randint(10, 20), minute=0)
            status_choice = random.choices(
                [StatusEnum.DELIVERED, StatusEnum.PAID, StatusEnum.PREPARING, StatusEnum.NEW, StatusEnum.CANCELLED],
                weights=[0.6, 0.1, 0.1, 0.1, 0.1],
            )[0]

            order = Order(
                tenant_id=moments.id,
                user_id=user.id,
                cake_config_id=config.id,
                status=status_choice,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                delivery_address="ул. Ленина, д. 10",
                comment="Позвонить за час до доставки" if random.random() > 0.5 else None,
                total_price=config.total_price,
                paid_at=datetime.utcnow() - timedelta(days=days_ago) if status_choice != StatusEnum.NEW else None,
            )
            session.add(order)
            await session.flush()

            session.add(OrderStatusLog(
                tenant_id=moments.id, order_id=order.id, status=StatusEnum.NEW,
            ))

            if status_choice == StatusEnum.DELIVERED:
                session.add(OrderStatusLog(
                    tenant_id=moments.id, order_id=order.id, status=StatusEnum.DELIVERED,
                    changed_by=admin.id,
                ))
            elif status_choice == StatusEnum.CANCELLED:
                session.add(OrderStatusLog(
                    tenant_id=moments.id, order_id=order.id, status=StatusEnum.CANCELLED,
                    changed_by=admin.id, comment="Клиент передумал",
                ))

        await session.commit()
        print("✅ Orders and status logs created")
        print()
        print("🎉 Done. Logins (password: admin123):")
        print("   SUPERADMIN : +79000000000  (X-Tenant: platform)")
        print("   moments adm: +79001111111  (X-Tenant: moments)")
        print("   bakery2 adm: +79002222222  (X-Tenant: bakery2)")


if __name__ == "__main__":
    asyncio.run(seed())