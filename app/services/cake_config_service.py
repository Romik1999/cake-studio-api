from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CakeConfig, CakeIngredient, Ingredient, Preset
from app.schemas import CakeConfigCreate, CakeConfigUpdate


class CakeConfigService:
    MAX_CUSTOM_INGREDIENTS = 5

    @staticmethod
    async def _calculate_price(
            session: AsyncSession,
            tenant_id: int,
            preset_id: int | None,
            dough_id: int | None,
            cake_ingredients,
    ) -> tuple[Decimal, Decimal, dict[int, Decimal]]:
        """Считает (base_price, total_price, price_map)."""
        if preset_id is not None:
            preset = (await session.execute(
                select(Preset).where(
                    Preset.id == preset_id,
                    Preset.tenant_id == tenant_id,
                )
            )).scalar_one_or_none()
            if preset is None:
                raise ValueError(f"Preset with id={preset_id} not found")
            return preset.price, preset.price, {}

        if dough_id is None:
            raise ValueError("dough_id is required for custom cake")

        ingredient_ids = {dough_id} | {ci.ingredient_id for ci in cake_ingredients}

        ingredients = (await session.execute(
            select(Ingredient).where(
                Ingredient.id.in_(ingredient_ids),
                Ingredient.tenant_id == tenant_id,
            )
        )).scalars().all()

        price_map: dict[int, Decimal] = {i.id: i.base_price for i in ingredients}

        missing = ingredient_ids - price_map.keys()
        if missing:
            raise ValueError(f"Ingredient(s) not found in tenant: {sorted(missing)}")

        base_price = sum(price_map.values(), Decimal("0"))
        return base_price, base_price, price_map

    @staticmethod
    async def get_all(
            session: AsyncSession,
            tenant_id: int,
            page: int = 1,
            limit: int = 10,
    ) -> tuple[list[CakeConfig], int]:
        base = select(CakeConfig).where(CakeConfig.tenant_id == tenant_id)

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
            tenant_id: int,
    ) -> CakeConfig | None:
        query = (
            select(CakeConfig)
            .where(CakeConfig.id == cake_config_id, CakeConfig.tenant_id == tenant_id)
            .options(
                selectinload(CakeConfig.cake_ingredients)
                .selectinload(CakeIngredient.ingredient),
                selectinload(CakeConfig.dough),
                selectinload(CakeConfig.preset),
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            session: AsyncSession,
            data: CakeConfigCreate,
            tenant_id: int,
    ) -> CakeConfig:
        if data.preset_id is not None and data.dough_id is not None:
            raise ValueError("Cannot use preset_id and dough_id together")
        if data.preset_id is None and data.dough_id is None:
            raise ValueError("Either preset_id or dough_id must be provided")
        if data.preset_id is not None and data.cake_ingredients:
            raise ValueError("cake_ingredients cannot be provided when preset_id is used")

        if (
                data.preset_id is None
                and len(data.cake_ingredients) > CakeConfigService.MAX_CUSTOM_INGREDIENTS
        ):
            raise ValueError(
                f"Max {CakeConfigService.MAX_CUSTOM_INGREDIENTS} custom ingredients allowed"
            )

        base_price, total_price, price_map = await CakeConfigService._calculate_price(
            session,
            tenant_id,
            data.preset_id,
            data.dough_id,
            data.cake_ingredients,
        )

        decoration_dict = data.decoration.model_dump() if data.decoration else None
        new_config = CakeConfig(
            dough_id=data.dough_id if data.preset_id is None else None,
            preset_id=data.preset_id,
            base_price=base_price,
            total_price=total_price,
            decoration=decoration_dict,
            tenant_id=tenant_id,
        )
        session.add(new_config)
        await session.flush()

        if data.preset_id is None and data.cake_ingredients:
            cake_ingredients_list = [
                CakeIngredient(
                    cake_config_id=new_config.id,
                    ingredient_id=ci.ingredient_id,
                    quantity=ci.quantity,
                    added_price=price_map[ci.ingredient_id],
                    sort_order=ci.sort_order,
                    tenant_id=tenant_id,
                )
                for ci in data.cake_ingredients
            ]
            session.add_all(cake_ingredients_list)
            await session.flush()

        return await CakeConfigService.get_by_id(session, new_config.id, tenant_id)

    @staticmethod
    async def update(
            session: AsyncSession,
            cake_config_id: int,
            data: CakeConfigUpdate,
            tenant_id: int,
    ) -> CakeConfig | None:
        config = await CakeConfigService.get_by_id(session, cake_config_id, tenant_id)
        if config is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        switched_to_preset = "preset_id" in update_data and update_data["preset_id"] is not None
        switched_to_dough = "dough_id" in update_data and update_data["dough_id"] is not None

        if switched_to_preset and switched_to_dough:
            raise ValueError("Cannot use preset_id and dough_id together")

        if switched_to_preset:
            if data.cake_ingredients:
                raise ValueError("cake_ingredients cannot be provided when preset_id is used")
            config.preset_id = update_data["preset_id"]
            config.dough_id = None
            for old_ci in list(config.cake_ingredients):
                await session.delete(old_ci)
            await session.flush()
        elif switched_to_dough:
            config.dough_id = update_data["dough_id"]
            config.preset_id = None

        if "decoration" in update_data:
            config.decoration = update_data["decoration"]

        if data.cake_ingredients is not None and config.preset_id is None:
            if len(data.cake_ingredients) > CakeConfigService.MAX_CUSTOM_INGREDIENTS:
                raise ValueError(
                    f"Max {CakeConfigService.MAX_CUSTOM_INGREDIENTS} custom ingredients allowed"
                )

            base_price, total_price, price_map = await CakeConfigService._calculate_price(
                session, tenant_id, None, config.dough_id, data.cake_ingredients,
            )

            for old_ci in list(config.cake_ingredients):
                await session.delete(old_ci)
            await session.flush()

            if data.cake_ingredients:
                new_ingredients = [
                    CakeIngredient(
                        cake_config_id=config.id,
                        ingredient_id=ci.ingredient_id,
                        quantity=ci.quantity,
                        added_price=price_map[ci.ingredient_id],
                        sort_order=ci.sort_order,
                        tenant_id=tenant_id,
                    )
                    for ci in data.cake_ingredients
                ]
                session.add_all(new_ingredients)
                await session.flush()
        else:
            base_price, total_price, price_map = await CakeConfigService._calculate_price(
                session, tenant_id, config.preset_id, config.dough_id, config.cake_ingredients,
            )

        config.base_price = base_price
        config.total_price = total_price

        await session.flush()
        return await CakeConfigService.get_by_id(session, config.id, tenant_id)

    @staticmethod
    async def delete(
            session: AsyncSession,
            cake_config_id: int,
            tenant_id: int,
    ) -> bool:
        config = await CakeConfigService.get_by_id(session, cake_config_id, tenant_id)
        if config is None:
            return False

        await session.delete(config)
        await session.flush()
        return True