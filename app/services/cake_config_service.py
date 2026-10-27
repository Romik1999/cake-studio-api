from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, InstrumentedAttribute

from app.models import CakeConfig, CakeIngredient, Ingredient, Preset
from app.schemas import CakeConfigCreate, CakeConfigUpdate


class CakeConfigService:
    MAX_CUSTOM_INGREDIENTS = 5

    @staticmethod
    async def _calculate_price(
            session: AsyncSession,
            preset_id: int | None,
            dough_id: int | None,
            cake_ingredients,
    ) -> tuple[InstrumentedAttribute[Decimal], InstrumentedAttribute[Decimal]]:
        """Считает (base_price, total_price)."""
        # Если выбран пресет — цена фиксирована, остальное игнорируется
        if preset_id is not None:
            preset = await session.get(Preset, preset_id)
            if preset is None:
                raise ValueError(f"Preset with id={preset_id} not found")
            return preset.price, preset.price

        # Кастомный сбор
        if dough_id is None:
            raise ValueError("dough_id is required for custom cake")

        dough = await session.get(Ingredient, dough_id)
        if dough is None:
            raise ValueError(f"Dough (ingredient) with id={dough_id} not found")

        base = dough.base_price

        for ci in cake_ingredients:
            ingredient = await session.get(Ingredient, ci.ingredient_id)
            if ingredient is None:
                raise ValueError(f"Ingredient with id={ci.ingredient_id} not found")
            base += ingredient.base_price

        return base, base

    # ==================== Чтение ====================

    @staticmethod
    async def get_all(
            session: AsyncSession,
            page: int = 1,
            limit: int = 10,
    ) -> tuple[list[CakeConfig], int]:
        base = select(CakeConfig)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            base.order_by(CakeConfig.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_by_id(
            session: AsyncSession,
            cake_config_id: int,
    ) -> CakeConfig | None:
        query = (
            select(CakeConfig)
            .where(CakeConfig.id == cake_config_id)
            .options(
                selectinload(CakeConfig.cake_ingredients).selectinload(CakeIngredient.ingredient),
                selectinload(CakeConfig.dough),
                selectinload(CakeConfig.preset),
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    # ==================== Создание ====================

    @staticmethod
    async def create(
            session: AsyncSession,
            data: CakeConfigCreate,
    ) -> CakeConfig:
        # Валидация: либо preset, либо dough
        if data.preset_id is None and data.dough_id is None:
            raise ValueError("Either preset_id or dough_id must be provided")

        # Валидация лимита (только для кастома)
        if (
                data.preset_id is None
                and len(data.cake_ingredients) > CakeConfigService.MAX_CUSTOM_INGREDIENTS
        ):
            raise ValueError(
                f"Max {CakeConfigService.MAX_CUSTOM_INGREDIENTS} custom ingredients allowed"
            )

        # Расчёт цены
        base_price, total_price = await CakeConfigService._calculate_price(
            session,
            preset_id=data.preset_id,
            dough_id=data.dough_id,
            cake_ingredients=data.cake_ingredients,
        )

        # Создаём конфиг
        decoration_dict = data.decoration.model_dump() if data.decoration else None
        new_config = CakeConfig(
            dough_id=None if data.preset_id else data.dough_id,
            preset_id=data.preset_id,
            base_price=base_price,
            total_price=total_price,
            decoration=decoration_dict,
        )
        session.add(new_config)
        await session.flush()

        # Кастомные ингредиенты — только если preset не выбран
        if data.preset_id is None and data.cake_ingredients:
            session.add_all([
                CakeIngredient(
                    cake_config_id=new_config.id,
                    ingredient_id=ci.ingredient_id,
                    quantity=ci.quantity,
                    added_price=ci.added_price,
                    sort_order=ci.sort_order,
                )
                for ci in data.cake_ingredients
            ])
            await session.flush()

        # Перезапрашиваем с подгруженными связями
        return await CakeConfigService.get_by_id(session, new_config.id)

    # ==================== Обновление ====================

    @staticmethod
    async def update(
            session: AsyncSession,
            cake_config_id: int,
            data: CakeConfigUpdate,
    ) -> CakeConfig | None:
        config = await CakeConfigService.get_by_id(session, cake_config_id)
        if config is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Скалярные поля
        if "dough_id" in update_data:
            config.dough_id = update_data["dough_id"]
        if "preset_id" in update_data:
            config.preset_id = update_data["preset_id"]
        if "decoration" in update_data:
            config.decoration = update_data["decoration"]

        # Пересборка кастомных ингредиентов
        if data.cake_ingredients is not None and config.preset_id is None:
            if len(data.cake_ingredients) > CakeConfigService.MAX_CUSTOM_INGREDIENTS:
                raise ValueError(
                    f"Max {CakeConfigService.MAX_CUSTOM_INGREDIENTS} custom ingredients allowed"
                )

            # Удаляем старые
            for old_ci in list(config.cake_ingredients):
                await session.delete(old_ci)
            await session.flush()

            # Создаём новые
            if data.cake_ingredients:
                session.add_all([
                    CakeIngredient(
                        cake_config_id=config.id,
                        ingredient_id=ci.ingredient_id,
                        quantity=ci.quantity,
                        added_price=ci.added_price,
                        sort_order=ci.sort_order,
                    )
                    for ci in data.cake_ingredients
                ])
                await session.flush()

            cake_ingredients_for_price = data.cake_ingredients
        else:
            cake_ingredients_for_price = config.cake_ingredients

        # Пересчёт цены
        base_price, total_price = await CakeConfigService._calculate_price(
            session,
            preset_id=config.preset_id,
            dough_id=config.dough_id,
            cake_ingredients=cake_ingredients_for_price,
        )
        config.base_price = base_price
        config.total_price = total_price

        await session.flush()
        return await CakeConfigService.get_by_id(session, config.id)

    # ==================== Удаление ====================

    @staticmethod
    async def delete(
            session: AsyncSession,
            cake_config_id: int,
    ) -> bool:
        config = await CakeConfigService.get_by_id(session, cake_config_id)
        if config is None:
            return False

        await session.delete(config)
        await session.flush()
        return True
