from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, DateTime, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CakeConfig(Base):
    __tablename__ = "cake_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Корж (если кастомный сбор)
    dough_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=True
    )

    # Пресет (если выбран готовый)
    preset_id: Mapped[int | None] = mapped_column(
        ForeignKey("presets.id", ondelete="RESTRICT"),
        nullable=True
    )

    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    decoration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Связь с промежуточной таблицей (ингредиенты торта)
    cake_ingredients: Mapped[list["CakeIngredient"]] = relationship(
        back_populates="cake_config",
        cascade="all, delete-orphan"
    )

    # Связь с коржом (объект Ingredient)
    dough: Mapped["Ingredient"] = relationship(
        foreign_keys=[dough_id]
    )

    # Связь с пресетом (объект Preset)
    preset: Mapped["Preset"] = relationship(
        foreign_keys=[preset_id]
    )