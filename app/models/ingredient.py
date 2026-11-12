from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Enum as SQLEnum, Numeric,
    func, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategoryEnum(str, Enum):
    DOUGH = "dough"
    FILLING = "filling"
    CREAM = "cream"
    DECORATION = "decoration"
    TOPPING = "topping"
    INSCRIPTION = "inscription"


class UnitEnum(str, Enum):
    GRAM = "gram"
    MILLILITER = "milliliter"
    PIECE = "piece"


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30))
    category: Mapped[CategoryEnum] = mapped_column(SQLEnum(CategoryEnum), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    unit: Mapped[UnitEnum] = mapped_column(SQLEnum(UnitEnum))
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(),
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    preset_ingredients: Mapped[list["PresetIngredient"]] = relationship(
        "PresetIngredient",
        primaryjoin="and_(foreign(PresetIngredient.tenant_id) == Ingredient.tenant_id, foreign(PresetIngredient.ingredient_id) == Ingredient.id)",
        viewonly=True,
    )
    cake_ingredients: Mapped[list["CakeIngredient"]] = relationship(
        "CakeIngredient",
        primaryjoin="and_(foreign(CakeIngredient.tenant_id) == Ingredient.tenant_id, foreign(CakeIngredient.ingredient_id) == Ingredient.id)",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'title', name='uq_ingredient_tenant_title'),
        UniqueConstraint('tenant_id', 'id', name='uq_ingredient_tenant_id'),
    )
