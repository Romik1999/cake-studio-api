from sqlalchemy import Integer, String, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PresetIngredient(Base):
    __tablename__ = "preset_ingredients"

    preset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    quantity: Mapped[str] = mapped_column(String(20))

    preset: Mapped["Preset"] = relationship(
        "Preset",
        primaryjoin="and_(foreign(PresetIngredient.tenant_id) == Preset.tenant_id, foreign(PresetIngredient.preset_id) == Preset.id)",
        viewonly=True,
    )
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        primaryjoin="and_(foreign(PresetIngredient.tenant_id) == Ingredient.tenant_id, foreign(PresetIngredient.ingredient_id) == Ingredient.id)",
        viewonly=True,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['tenant_id', 'preset_id'],
            ['presets.tenant_id', 'presets.id'],
            ondelete='CASCADE',
            name='fk_preset_ingredient_tenant_preset',
        ),
        ForeignKeyConstraint(
            ['tenant_id', 'ingredient_id'],
            ['ingredients.tenant_id', 'ingredients.id'],
            ondelete='RESTRICT',
            name='fk_preset_ingredient_tenant_ingredient',
        ),
    )