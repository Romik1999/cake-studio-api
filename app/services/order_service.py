from datetime import date, datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order, StatusEnum, User, OrderStatusLog, CakeConfig, CakeIngredient
from app.schemas import OrderCreate
from app.services.cake_config_service import CakeConfigService
from app.services.user_service import UserService


class OrderService:
    @staticmethod
    async def create(session: AsyncSession, data: OrderCreate) -> Order:
        current_user = await UserService.get_by_phone(session, data.user_phone)

        if current_user is None:
            new_user = User(name=data.user_name, phone=data.user_phone)
            session.add(new_user)
            await session.flush()
            current_user = new_user

        cake_config = await CakeConfigService.get_by_id(session, data.cake_config_id)
        if cake_config is None:
            raise ValueError("Cake config not found")

        order = Order(
            user_id=current_user.id,
            cake_config_id=cake_config.id,
            total_price=cake_config.total_price,
            delivery_date=data.delivery_date,
            delivery_time=data.delivery_time,
            delivery_address=data.delivery_address,
            comment=data.comment
        )

        session.add(order)
        await session.flush()

        log = OrderStatusLog(order_id=order.id, status=StatusEnum.NEW)

        session.add(log)
        await session.flush()

        return await OrderService.get_by_id(session, order.id)

    @staticmethod
    async def get_all(
            session: AsyncSession,
            page: int = 1,
            limit: int = 10,
            status_filter: StatusEnum | None = None,
            date_filter: date | None = None,
    ) -> tuple[list[Order], int]:
        base = select(Order)

        if status_filter is not None:
            base = base.where(Order.status == status_filter)

        if date_filter is not None:
            base = base.where(Order.delivery_date == date_filter)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.order_by(Order.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_user_orders(
            session: AsyncSession,
            user_id: int,
            page: int = 1,
            limit: int = 10,
            status_filter: StatusEnum | None = None,
            date_filter: date | None = None
    ) -> tuple[list[Order], int]:
        base = select(Order).where(Order.user_id == user_id)

        if status_filter is not None:
            base = base.where(Order.status == status_filter)

        if date_filter is not None:
            base = base.where(Order.delivery_date == date_filter)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.order_by(Order.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

        pass

    @staticmethod
    async def get_by_id(session: AsyncSession, order_id: int) -> Order | None:
        query = select(Order).where(Order.id == order_id).options(
            # Ветка 1: cake_config → cake_ingredients → ingredient
            selectinload(Order.cake_config)
            .selectinload(CakeConfig.cake_ingredients)
            .selectinload(CakeIngredient.ingredient),

            # Ветка 2: user
            selectinload(Order.user),

            # Ветка 3: status_log → changed_by_user
            selectinload(Order.status_log)
            .selectinload(OrderStatusLog.changed_by_user),
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_order(
            session: AsyncSession,
            order_id: int,
            new_status: StatusEnum,
            changed_by_id: int,
            comment: str | None
    ) -> Order | None:

        order = await OrderService.get_by_id(session, order_id)

        if order is None:
            return None

        if order.status == StatusEnum.DELIVERED and new_status == StatusEnum.NEW:
            raise ValueError("Delivered order already delivered")

        order.status = new_status

        if new_status == StatusEnum.PAID:
            order.paid_at = datetime.now(timezone.utc)

        log = OrderStatusLog(order_id=order.id, status=new_status, changed_by=changed_by_id, comment=comment)
        session.add(log)
        await session.flush()

        return await OrderService.get_by_id(session, order_id)

    @staticmethod
    async def cancel(
            session: AsyncSession,
            order_id: int,
            changed_by_id: int,
            comment: str | None
    ) -> Order | None:

        return await OrderService.update_order(
            session=session,
            order_id=order_id,
            new_status=StatusEnum.CANCELLED,
            changed_by_id=changed_by_id,
            comment=comment
        )
