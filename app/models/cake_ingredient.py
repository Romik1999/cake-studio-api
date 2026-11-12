from decimal import Decimal

from sqlalchemy import (
    String, Numeric, Integer, ForeignKey, ForeignKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CakeIngredient(Base):
    __tablename__ = "cake_ingredients"

    cake_config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    quantity: Mapped[str] = mapped_column(String(20))
    added_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    cake_config: Mapped["CakeConfig"] = relationship(
        "CakeConfig",
        primaryjoin="and_(foreign(CakeIngredient.tenant_id) == CakeConfig.tenant_id, foreign(CakeIngredient.cake_config_id) == CakeConfig.id)",
        viewonly=True,
    )
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        primaryjoin="and_(foreign(CakeIngredient.tenant_id) == Ingredient.tenant_id, foreign(CakeIngredient.ingredient_id) == Ingredient.id)",
        viewonly=True,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['tenant_id', 'cake_config_id'],
            ['cake_configs.tenant_id', 'cake_configs.id'],
            ondelete='CASCADE',
            name='fk_cake_ingredient_tenant_config',
        ),
        ForeignKeyConstraint(
            ['tenant_id', 'ingredient_id'],
            ['ingredients.tenant_id', 'ingredients.id'],
            ondelete='RESTRICT',
            name='fk_cake_ingredient_tenant_ingredient',
        ),
    )