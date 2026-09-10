from datetime import datetime, time, date
from decimal import Decimal
from enum import Enum

from app.database import Base

from sqlalchemy import String, Integer, DateTime, Numeric, func, ForeignKey, Enum as SQLEnum, Time, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StatusEnum(str, Enum):
    NEW = "new"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True
    )
    cake_config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cake_configs.id", ondelete="RESTRICT")
    )
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum),
        default=StatusEnum.NEW,
        index=True
    )
    delivery_date: Mapped[date] = mapped_column(Date, index=True)
    delivery_time: Mapped[time] = mapped_column(Time)
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=True)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    cake_config: Mapped["CakeConfig"] = relationship("CakeConfig", back_populates="order")
    status_log: Mapped[list["OrderStatusLog"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )