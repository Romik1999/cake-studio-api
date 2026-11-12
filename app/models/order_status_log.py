from datetime import datetime

from sqlalchemy import (
    String, Integer, DateTime, func, ForeignKey, ForeignKeyConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.order import StatusEnum


class OrderStatusLog(Base):
    __tablename__ = "order_status_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    order: Mapped["Order"] = relationship(
        "Order",
        primaryjoin="and_(foreign(OrderStatusLog.tenant_id) == Order.tenant_id, foreign(OrderStatusLog.order_id) == Order.id)",
        viewonly=True,
    )
    changed_by_user: Mapped["User | None"] = relationship(
        "User", foreign_keys=[changed_by], viewonly=True,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['tenant_id', 'order_id'],
            ['orders.tenant_id', 'orders.id'],
            ondelete='CASCADE',
            name='fk_order_status_log_tenant_order',
        ),
    )