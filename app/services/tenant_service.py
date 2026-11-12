from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Tenant


class TenantService:
    @staticmethod
    async def get_by_domain(session: AsyncSession, domain: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.domain == domain)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(session: AsyncSession, slug: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.slug == slug)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        session: AsyncSession,
        is_active: bool | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Tenant], int]:
        base = select(Tenant)

        if is_active is not None:
            base = base.where(Tenant.is_active == is_active)

        # Считаем total через подзапрос
        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        # Пагинация и сортировка
        query = base.order_by(Tenant.created_at).offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_by_id(session: AsyncSession, tenant_id: int) -> Tenant | None:
        query = select(Tenant).where(Tenant.id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
