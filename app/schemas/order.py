from datetime import datetime, date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import StatusEnum
from app.schemas.user import UserResponse
from app.schemas.cake_config import CakeConfigDetail

class OrderStatusLogResponse(BaseModel):
    id: int
    status: StatusEnum
    changed_at: datetime
    changed_by_user: UserResponse | None = None
    comment: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    cake_config_id: int
    user_phone: str = Field(min_length=10, max_length=20, pattern=r"^\+?[0-9]{10,15}$")
    user_name: str = Field(min_length=3, max_length=30)
    delivery_date: date
    delivery_time: time
    delivery_address: str | None = Field(default=None, max_length=500)
    comment: str | None = Field(default=None, max_length=500)


class OrderResponse(BaseModel):
    id: int
    status: StatusEnum
    total_price: Decimal = Field(ge=0)
    delivery_date: date
    delivery_time: time
    delivery_address: str | None = None
    comment: str | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetail(OrderResponse):
    user: UserResponse
    cake_config: CakeConfigDetail
    status_log: list[OrderStatusLogResponse]


class OrderStatusUpdate(BaseModel):
    status: StatusEnum
    comment: str | None = Field(default=None, max_length=500)
