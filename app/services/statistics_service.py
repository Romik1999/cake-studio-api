from datetime import date
from decimal import Decimal

from sqlalchemy import select, func, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Order,
    StatusEnum,
    User,
    Ingredient,
    CakeIngredient,
    PresetIngredient,
)
from app.schemas import (
    DailySalesItem,
    PopularIngredientItem,
    FrequentCustomerItem,
)


class StatisticsService:

    # ==================== 1. Продажи по дням ====================

    @staticmethod
    async def get_daily_sales(
            session: AsyncSession,
            start_date: date,
            end_date: date,
    ) -> tuple[list[DailySalesItem], Decimal, int]:
        query = (
            select(
                Order.delivery_date,
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_price).label("total_revenue"),
            )
            .where(Order.status == StatusEnum.DELIVERED)
            .where(Order.delivery_date >= start_date)
            .where(Order.delivery_date <= end_date)
            .group_by(Order.delivery_date)
            .order_by(Order.delivery_date.asc())
        )

        result = await session.execute(query)
        rows = result.all()

        items = [
            DailySalesItem(
                date=row.delivery_date,
                orders_count=row.orders_count,
                total_revenue=row.total_revenue or Decimal("0"),
            )
            for row in rows
        ]

        total_revenue = sum((i.total_revenue for i in items), Decimal("0"))
        total_orders = sum(i.orders_count for i in items)

        return items, total_revenue, total_orders

    # ==================== 2. Популярные ингредиенты ====================

    @staticmethod
    async def get_popular_ingredients(
            session: AsyncSession,
            limit: int = 10,
    ) -> list[PopularIngredientItem]:
        # Объединяем usage из cake_ingredients и preset_ingredients
        cake_usage = select(CakeIngredient.ingredient_id.label("ingredient_id"))
        preset_usage = select(PresetIngredient.ingredient_id.label("ingredient_id"))

        union_query = union_all(cake_usage, preset_usage).subquery()

        query = (
            select(
                Ingredient.id,
                Ingredient.title,
                Ingredient.category,
                func.count(union_query.c.ingredient_id).label("usage_count"),
            )
            .join(union_query, Ingredient.id == union_query.c.ingredient_id)
            .group_by(Ingredient.id, Ingredient.title, Ingredient.category)
            .order_by(func.count(union_query.c.ingredient_id).desc())
            .limit(limit)
        )

        result = await session.execute(query)
        rows = result.all()

        return [
            PopularIngredientItem(
                ingredient_id=row.id,
                title=row.title,
                category=row.category,
                usage_count=row.usage_count,
            )
            for row in rows
        ]

    # ==================== 3. Выручка ====================

    @staticmethod
    async def get_revenue(
            session: AsyncSession,
            start_date: date,
            end_date: date,
    ) -> tuple[Decimal, Decimal, int]:
        query = (
            select(
                func.sum(Order.total_price).label("total_revenue"),
                func.count(Order.id).label("orders_count"),
            )
            .where(Order.status == StatusEnum.DELIVERED)
            .where(Order.delivery_date >= start_date)
            .where(Order.delivery_date <= end_date)
        )

        result = await session.execute(query)
        row = result.one()

        total_revenue = row.total_revenue or Decimal("0")
        orders_count = row.orders_count or 0

        avg_order_value = (
            total_revenue / orders_count if orders_count > 0 else Decimal("0")
        )

        return total_revenue, avg_order_value, orders_count

    # ==================== 4. Частые клиенты ====================

    @staticmethod
    async def get_frequent_customers(
            session: AsyncSession,
            limit: int = 10,
    ) -> list[FrequentCustomerItem]:
        query = (
            select(
                User.id,
                User.name,
                User.phone,
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_price).label("total_spent"),
            )
            .join(Order, Order.user_id == User.id)
            .where(Order.status != StatusEnum.CANCELLED)
            .group_by(User.id, User.name, User.phone)
            .order_by(func.count(Order.id).desc())
            .limit(limit)
        )

        result = await session.execute(query)
        rows = result.all()

        return [
            FrequentCustomerItem(
                user_id=row.id,
                name=row.name,
                phone=row.phone,
                orders_count=row.orders_count,
                total_spent=row.total_spent or Decimal("0"),
            )
            for row in rows
        ]

    # ==================== 5. Отменённые заказы ====================

    @staticmethod
    async def get_cancelled_orders(
            session: AsyncSession,
            page: int = 1,
            limit: int = 10,
    ) -> tuple[list[Order], int]:
        base = select(Order).where(Order.status == StatusEnum.CANCELLED)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.options(selectinload(Order.user))
            .order_by(Order.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total
