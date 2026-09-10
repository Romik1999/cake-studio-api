from datetime import datetime

from app.database import Base

from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.order import StatusEnum


class OrderStatusLog(Base):
    __tablename__ = "order_status_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Связь с заказом (обратная к Order.status_log)
    order: Mapped["Order"] = relationship(back_populates="status_log")

    # Связь с пользователем, который изменил статус
    changed_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[changed_by]
    )
