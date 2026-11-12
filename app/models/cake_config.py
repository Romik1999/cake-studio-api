from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, DateTime, func, ForeignKey, ForeignKeyConstraint,
    Numeric, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CakeConfig(Base):
    __tablename__ = "cake_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    dough_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preset_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    decoration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(),
    )

    cake_ingredients: Mapped[list["CakeIngredient"]] = relationship(
        "CakeIngredient",
        primaryjoin="and_(foreign(CakeIngredient.tenant_id) == CakeConfig.tenant_id, foreign(CakeIngredient.cake_config_id) == CakeConfig.id)",
        viewonly=True,
    )
    dough: Mapped["Ingredient | None"] = relationship(
        "Ingredient",
        primaryjoin="and_(foreign(CakeConfig.tenant_id) == Ingredient.tenant_id, foreign(CakeConfig.dough_id) == Ingredient.id)",
        viewonly=True,
    )
    preset: Mapped["Preset | None"] = relationship(
        "Preset",
        primaryjoin="and_(foreign(CakeConfig.tenant_id) == Preset.tenant_id, foreign(CakeConfig.preset_id) == Preset.id)",
        viewonly=True,
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        primaryjoin="and_(foreign(Order.tenant_id) == CakeConfig.tenant_id, foreign(Order.cake_config_id) == CakeConfig.id)",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint(
            '(dough_id IS NOT NULL) <> (preset_id IS NOT NULL)',
            name='ck_cake_config_exactly_one_source',
        ),
        UniqueConstraint('tenant_id', 'id', name='uq_cake_config_tenant_id'),
        ForeignKeyConstraint(
            ['tenant_id', 'dough_id'],
            ['ingredients.tenant_id', 'ingredients.id'],
            ondelete='RESTRICT',
            name='fk_cake_config_tenant_dough',
        ),
        ForeignKeyConstraint(
            ['tenant_id', 'preset_id'],
            ['presets.tenant_id', 'presets.id'],
            ondelete='RESTRICT',
            name='fk_cake_config_tenant_preset',
        ),
    )