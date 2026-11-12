from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Numeric, func, ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Preset(Base):
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=1)
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
        primaryjoin="and_(foreign(PresetIngredient.tenant_id) == Preset.tenant_id, foreign(PresetIngredient.preset_id) == Preset.id)",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'title', name='uq_preset_tenant_title'),
        UniqueConstraint('tenant_id', 'id', name='uq_preset_tenant_id'),
    )