from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Preset, PresetIngredient
from app.schemas import PresetCreate, PresetUpdate


class PresetService:
    @staticmethod
    async def get_all(
            session: AsyncSession,
            is_active: bool | None = None,
            page: int = 1,
            limit: int = 10
    ) -> tuple[list[Preset], int]:
        base = select(Preset)

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
    async def get_by_id(session: AsyncSession, preset_id: int) -> Preset | None:
        query = (select(Preset)
        .where(Preset.id == preset_id)
        .options(
            selectinload(Preset.preset_ingredients)
            .selectinload(PresetIngredient.ingredient)
        )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: PresetCreate) -> Preset:
        # 1. Создаём сам пресет без ингредиентов
        preset_data = data.model_dump(exclude={"preset_ingredients"})
        new_preset = Preset(**preset_data)
        session.add(new_preset)
        await session.flush()  # получаем new_preset.id

        # 2. Создаём PresetIngredient для каждого ингредиента
        preset_ingredients = [
            PresetIngredient(
                preset_id=new_preset.id,
                ingredient_id=item.ingredient_id,
                quantity=item.quantity,
            )
            for item in data.preset_ingredients
        ]
        session.add_all(preset_ingredients)
        await session.flush()

        # 3. Возвращаем пресет с подгруженными связями
        query = (
            select(Preset)
            .where(Preset.id == new_preset.id)
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
    ) -> Preset | None:

        # 1. Находим пресет (с подгрузкой ингредиентов)
        current_preset = await PresetService.get_by_id(session, preset_id)
        if current_preset is None:
            return None

        # 2. Обновляем скалярные поля (без preset_ingredients)
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"preset_ingredients"},
        )
        for field, value in update_data.items():
            setattr(current_preset, field, value)

        # 3. Если preset_ingredients передан — пересобираем состав
        if "preset_ingredients" in data.model_dump(exclude_unset=True):
            # Удаляем старые связи
            for old_pi in list(current_preset.preset_ingredients):
                await session.delete(old_pi)

            # Создаём новые
            new_preset_ingredients = [
                PresetIngredient(
                    preset_id=current_preset.id,
                    ingredient_id=item.ingredient_id,
                    quantity=item.quantity,
                )
                for item in data.preset_ingredients
            ]
            session.add_all(new_preset_ingredients)

        await session.flush()

        # 4. Перезапрашиваем с подгрузкой актуального состава
        query = (
            select(Preset)
            .where(Preset.id == current_preset.id)
            .options(
                selectinload(Preset.preset_ingredients)
                .selectinload(PresetIngredient.ingredient)
            )
        )
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def delete(session: AsyncSession, preset_id: int) -> bool:
        current_preset = await PresetService.get_by_id(session, preset_id)
        if current_preset is None:
            return False

        await session.delete(current_preset)
        await session.flush()
        return True