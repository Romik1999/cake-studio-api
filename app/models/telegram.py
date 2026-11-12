from datetime import datetime

from sqlalchemy import (
    String, Integer, Boolean, DateTime, func, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TelegramRecipient(Base):
    __tablename__ = "telegram_recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('tenant_id', 'chat_id', name='uq_telegram_tenant_chat'),
    )