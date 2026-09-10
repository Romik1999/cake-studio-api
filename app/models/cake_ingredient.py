from decimal import Decimal

from sqlalchemy import String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CakeIngredient(Base):
    __tablename__ = "cake_ingredients"

    cake_config_id: Mapped[int] = mapped_column(
        ForeignKey("cake_configs.id", ondelete="CASCADE"),
        primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        primary_key=True
    )
    quantity: Mapped[str] = mapped_column(String(20))
    added_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Связь с конфигом (обратная к CakeConfig.cake_ingredients)
    cake_config: Mapped["CakeConfig"] = relationship(back_populates="cake_ingredients")

    # Связь с ингредиентом (обратная к Ingredient.cake_ingredients)
    ingredient: Mapped["Ingredient"] = relationship(back_populates="cake_ingredients")