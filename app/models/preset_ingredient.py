from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PresetIngredient(Base):
    __tablename__ = "preset_ingredients"

    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True)
    quantity: Mapped[str] = mapped_column(String(20))  # строка, например "200g"

    # Связи к основным моделям
    preset: Mapped["Preset"] = relationship(back_populates="preset_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="preset_ingredients")