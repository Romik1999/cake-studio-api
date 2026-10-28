from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import CategoryEnum
from app.schemas.order import OrderResponse


# ==== Ежедневные продажи ====

class DailySalesItem(BaseModel):
    date: date
    orders_count: int
    total_revenue: Decimal

    model_config = ConfigDict(from_attributes=True)


class DailySalesResponse(BaseModel):
    items: list[DailySalesItem] = Field(default_factory=list)
    total_revenue: Decimal = Field(ge=0)
    total_orders: int = Field(ge=0)


# ==== Популярные ингредиенты ====

class PopularIngredientItem(BaseModel):
    ingredient_id: int
    title: str
    category: CategoryEnum
    usage_count: int

    model_config = ConfigDict(from_attributes=True)


class PopularIngredientsResponse(BaseModel):
    items: list[PopularIngredientItem] = Field(default_factory=list)


# ==== Выручка ====

class RevenueResponse(BaseModel):
    total_revenue: Decimal = Field(ge=0)
    avg_order_value: Decimal = Field(ge=0)
    orders_count: int = Field(ge=0)


# ==== Частые клиенты ====

class FrequentCustomerItem(BaseModel):
    user_id: int
    name: str
    phone: str
    orders_count: int
    total_spent: Decimal

    model_config = ConfigDict(from_attributes=True)


class FrequentCustomersResponse(BaseModel):
    items: list[FrequentCustomerItem] = Field(default_factory=list)


# ==== Отменённые заказы ====

class CancelledOrdersResponse(BaseModel):
    total_cancelled: int = Field(ge=0)
    items: list[OrderResponse] = Field(default_factory=list)
