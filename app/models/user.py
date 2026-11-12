from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String, Integer, DateTime, func, ForeignKey, UniqueConstraint, Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True,
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(),
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        primaryjoin="and_(foreign(Order.tenant_id) == User.tenant_id, foreign(Order.user_id) == User.id)",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'phone', name='uq_user_tenant_phone'),
        UniqueConstraint('tenant_id', 'email', name='uq_user_tenant_email'),
        UniqueConstraint('tenant_id', 'id', name='uq_user_tenant_id'),
    )