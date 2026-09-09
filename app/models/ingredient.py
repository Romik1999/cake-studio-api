from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum, Numeric, func
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
    title: Mapped[str] = mapped_column(String(30), unique=True)
    category: Mapped[CategoryEnum] = mapped_column(SQLEnum(CategoryEnum), index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    unit: Mapped[UnitEnum] = mapped_column(SQLEnum(UnitEnum))
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Связь с промежуточной таблицей
    preset_ingredients: Mapped[list["PresetIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )