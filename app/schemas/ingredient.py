from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, PositiveInt, Field, ConfigDict

from app.models import CategoryEnum, UnitEnum


class IngredientBase(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    category: CategoryEnum
    image_url: str | None = None
    description: str | None = Field(default=None, max_length=1000)
    unit: UnitEnum
    base_price: Decimal = Field(ge=0)
    sort_order: PositiveInt = Field(ge=1, le=10)
    is_active: bool = True


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=30)
    category: CategoryEnum | None = None
    image_url: str | None = None
    description: str | None = Field(default=None, max_length=1000)
    unit: UnitEnum | None = None
    base_price: Decimal | None = Field(default=None, ge=0)
    sort_order: PositiveInt | None = Field(default=None, ge=1, le=10)
    is_active: bool | None = None


class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
