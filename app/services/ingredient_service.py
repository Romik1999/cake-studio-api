from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ingredient, CategoryEnum
from app.schemas import IngredientCreate, IngredientUpdate


class IngredientService:

    @staticmethod
    async def get_all(
            session: AsyncSession,
            category: CategoryEnum | None = None,
            is_active: bool | None = None,
            page: int = 1,
            limit: int = 10,
    ) -> tuple[list[Ingredient], int]:
        """Вернуть список ингредиентов с фильтрами и общее количество."""
        base = select(Ingredient)

        if category is not None:
            base = base.where(Ingredient.category == category)
        if is_active is not None:
            base = base.where(Ingredient.is_active == is_active)

        # Считаем total через подзапрос
        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        # Пагинация и сортировка
        query = (
            base.order_by(Ingredient.sort_order)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_by_id(session: AsyncSession, ingredient_id: int) -> Ingredient | None:
        query = select(Ingredient).where(Ingredient.id == ingredient_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: IngredientCreate) -> Ingredient:
        new_ingredient = Ingredient(**data.model_dump())
        session.add(new_ingredient)
        await session.flush()  # получаем id, created_at, updated_at
        await session.refresh(new_ingredient)
        return new_ingredient

    @staticmethod
    async def update(
            session: AsyncSession,
            ingredient_id: int,
            data: IngredientUpdate,
    ) -> Ingredient | None:
        ingredient = await IngredientService.get_by_id(session, ingredient_id)
        if ingredient is None:
            return None

        # exclude_unset=True — берём только те поля, которые клиент реально передал
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ingredient, field, value)

        await session.flush()
        await session.refresh(ingredient)
        return ingredient

    @staticmethod
    async def delete(session: AsyncSession, ingredient_id: int) -> bool:
        ingredient = await IngredientService.get_by_id(session, ingredient_id)
        if ingredient is None:
            return False

        await session.delete(ingredient)
        await session.flush()
        return True
