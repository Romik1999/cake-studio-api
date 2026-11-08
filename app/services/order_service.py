from datetime import date, datetime, timezone

from sqlalchemy import select, func, or_
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
    def _apply_filters_and_sorting(
            base,
            status: list[StatusEnum] | None,
            created_from: date | None,
            created_to: date | None,
            search: str | None,
            sort_by: str | None,
            sort_order: str | None
    ):
        """Вспомогательный метод для применения фильтров к запросу."""

        # 1. Поиск (по имени, телефону или ID)
        if search:
            base = base.join(Order.user)
            search_conditions = [
                User.name.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            ]
            if search.isdigit():
                search_conditions.append(Order.id == int(search))

            base = base.where(or_(*search_conditions))

        # 2. Фильтр по статусам (мультиселект)
        if status:
            base = base.where(Order.status.in_(status))

        # 3. Фильтр по дате создания
        if created_from:
            base = base.where(func.date(Order.created_at) >= created_from)
        if created_to:
            base = base.where(func.date(Order.created_at) <= created_to)

        # 4. Сортировка (защита от SQL-инъекций через белый список)
        sort_mapping = {
            "id": Order.id,
            "total_price": Order.total_price,
            "created_at": Order.created_at,
            "delivery_date": Order.delivery_date,
        }

        if sort_by and sort_by in sort_mapping:
            column = sort_mapping[sort_by]
            if sort_order == "desc":
                base = base.order_by(column.desc())
            else:
                base = base.order_by(column.asc())
        else:
            # Дефолтная сортировка
            base = base.order_by(Order.created_at.desc())

        return base

    @staticmethod
    async def get_all(
            session: AsyncSession,
            page: int = 1,
            limit: int = 10,
            status: list[StatusEnum] | None = None,
            created_from: date | None = None,
            created_to: date | None = None,
            search: str | None = None,
            sort_by: str | None = None,
            sort_order: str | None = None,
    ) -> tuple[list[Order], int]:

        base = select(Order)
        base = OrderService._apply_filters_and_sorting(
            base, status, created_from, created_to, search, sort_by, sort_order
        )

        # Считаем total (используем distinct, если был join при поиске)
        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.offset((page - 1) * limit)
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
            status: list[StatusEnum] | None = None,
            created_from: date | None = None,
            created_to: date | None = None,
            search: str | None = None,
            sort_by: str | None = None,
            sort_order: str | None = None,
    ) -> tuple[list[Order], int]:

        base = select(Order).where(Order.user_id == user_id)
        base = OrderService._apply_filters_and_sorting(
            base, status, created_from, created_to, search, sort_by, sort_order
        )

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_by_id(session: AsyncSession, order_id: int) -> Order | None:
        query = select(Order).where(Order.id == order_id).options(
            selectinload(Order.user),
            selectinload(Order.status_log).selectinload(OrderStatusLog.changed_by_user),
            selectinload(Order.cake_config).selectinload(CakeConfig.cake_ingredients).selectinload(
                CakeIngredient.ingredient),
            selectinload(Order.cake_config).selectinload(CakeConfig.dough),
            selectinload(Order.cake_config).selectinload(CakeConfig.preset),
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