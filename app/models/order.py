from datetime import datetime, time, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    String, Integer, DateTime, Numeric, func, ForeignKey, ForeignKeyConstraint,
    Enum as SQLEnum, Time, Date, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatusEnum(str, Enum):
    NEW = "new"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    cake_config_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum), default=StatusEnum.NEW, index=True,
    )
    delivery_date: Mapped[date] = mapped_column(Date, index=True)
    delivery_time: Mapped[time] = mapped_column(Time)
    delivery_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(
        "User",
        primaryjoin="and_(foreign(Order.tenant_id) == User.tenant_id, foreign(Order.user_id) == User.id)",
        viewonly=True,
    )
    cake_config: Mapped["CakeConfig"] = relationship(
        "CakeConfig",
        primaryjoin="and_(foreign(Order.tenant_id) == CakeConfig.tenant_id, foreign(Order.cake_config_id) == CakeConfig.id)",
        viewonly=True,
    )
    status_log: Mapped[list["OrderStatusLog"]] = relationship(
        "OrderStatusLog",
        primaryjoin="and_(foreign(OrderStatusLog.tenant_id) == Order.tenant_id, foreign(OrderStatusLog.order_id) == Order.id)",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'id', name='uq_order_tenant_id'),
        ForeignKeyConstraint(
            ['tenant_id', 'user_id'],
            ['users.tenant_id', 'users.id'],
            ondelete='RESTRICT',
            name='fk_order_tenant_user',
        ),
        ForeignKeyConstraint(
            ['tenant_id', 'cake_config_id'],
            ['cake_configs.tenant_id', 'cake_configs.id'],
            ondelete='RESTRICT',
            name='fk_order_tenant_cake_config',
        ),
    )