from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, PositiveInt, ConfigDict

from app.schemas.ingredient import IngredientResponse


class PresetBase(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    sort_order: PositiveInt = Field(ge=1, le=10)


class PresetIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: str = Field(max_length=20)


class PresetCreate(PresetBase):
    preset_ingredients: list[PresetIngredientCreate] = Field(default_factory=list)


class PresetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=30)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    sort_order: PositiveInt | None = Field(default=None, ge=1, le=10)
    preset_ingredients: list[PresetIngredientCreate] | None = None


class PresetResponse(PresetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PresetIngredientDetail(BaseModel):
    ingredient_id: int
    quantity: str = Field(max_length=20)
    ingredient: IngredientResponse

    model_config = ConfigDict(from_attributes=True)


class PresetDetail(PresetResponse):
    preset_ingredients: list[PresetIngredientDetail] = Field(default_factory=list)