from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Preset, PresetIngredient, Ingredient
from app.schemas import PresetCreate, PresetUpdate


class PresetService:
    @staticmethod
    async def get_all(
            session: AsyncSession,
            tenant_id: int,
            is_active: bool | None = None,
            page: int = 1,
            limit: int = 10
    ) -> tuple[list[Preset], int]:
        base = select(Preset).where(Preset.tenant_id == tenant_id)

        if is_active is not None:
            base = base.where(Preset.is_active == is_active)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.order_by(Preset.sort_order)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_by_id(session: AsyncSession, preset_id: int, tenant_id: int) -> Preset | None:
        query = (
            select(Preset)
            .where(Preset.id == preset_id, Preset.tenant_id == tenant_id)
            .options(
                selectinload(Preset.preset_ingredients)
                .selectinload(PresetIngredient.ingredient)
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: PresetCreate, tenant_id: int) -> Preset:
        preset_data = data.model_dump(exclude={"preset_ingredients"})
        new_preset = Preset(**preset_data, tenant_id=tenant_id)
        session.add(new_preset)
        await session.flush()

        if data.preset_ingredients:
            ingredient_ids = {item.ingredient_id for item in data.preset_ingredients}
            found = (await session.execute(
                select(Ingredient.id).where(
                    Ingredient.id.in_(ingredient_ids),
                    Ingredient.tenant_id == tenant_id,
                )
            )).scalars().all()
            missing = ingredient_ids - set(found)
            if missing:
                raise ValueError(f"Ingredient(s) not found in tenant: {sorted(missing)}")

            preset_ingredients = [
                PresetIngredient(
                    preset_id=new_preset.id,
                    ingredient_id=item.ingredient_id,
                    quantity=item.quantity,
                    tenant_id=tenant_id,
                )
                for item in data.preset_ingredients
            ]
            session.add_all(preset_ingredients)
            await session.flush()

        query = (
            select(Preset)
            .where(Preset.id == new_preset.id, Preset.tenant_id == tenant_id)
            .options(
                selectinload(Preset.preset_ingredients)
                .selectinload(PresetIngredient.ingredient)
            )
        )
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update(
            session: AsyncSession,
            preset_id: int,
            data: PresetUpdate,
            tenant_id: int
    ) -> Preset | None:
        current_preset = await PresetService.get_by_id(session, preset_id, tenant_id)
        if current_preset is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"preset_ingredients"},
        )
        for field, value in update_data.items():
            setattr(current_preset, field, value)

        if data.preset_ingredients is not None:
            for old_pi in list(current_preset.preset_ingredients):
                await session.delete(old_pi)

            if data.preset_ingredients:
                ingredient_ids = {item.ingredient_id for item in data.preset_ingredients}
                found = (await session.execute(
                    select(Ingredient.id).where(
                        Ingredient.id.in_(ingredient_ids),
                        Ingredient.tenant_id == tenant_id,
                    )
                )).scalars().all()
                missing = ingredient_ids - set(found)
                if missing:
                    raise ValueError(f"Ingredient(s) not found in tenant: {sorted(missing)}")

                new_preset_ingredients = [
                    PresetIngredient(
                        preset_id=current_preset.id,
                        ingredient_id=item.ingredient_id,
                        quantity=item.quantity,
                        tenant_id=tenant_id,
                    )
                    for item in data.preset_ingredients
                ]
                session.add_all(new_preset_ingredients)

        await session.flush()

        query = (
            select(Preset)
            .where(Preset.id == current_preset.id, Preset.tenant_id == tenant_id)
            .options(
                selectinload(Preset.preset_ingredients)
                .selectinload(PresetIngredient.ingredient)
            )
        )
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def delete(session: AsyncSession, preset_id: int, tenant_id: int) -> bool:
        current_preset = await PresetService.get_by_id(session, preset_id, tenant_id)
        if current_preset is None:
            return False

        await session.delete(current_preset)
        await session.flush()
        return True