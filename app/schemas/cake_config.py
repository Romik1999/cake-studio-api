from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.ingredient import IngredientResponse
from app.schemas.preset import PresetResponse


class CakeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: str = Field(max_length=20)
    added_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    sort_order: int = Field(default=0, ge=0)


class CakeIngredientDetail(BaseModel):
    ingredient_id: int
    quantity: str = Field(max_length=20)
    added_price: Decimal
    sort_order: int
    ingredient: IngredientResponse

    model_config = ConfigDict(from_attributes=True)


class DecorationSchema(BaseModel):
    type: str = Field(description="Тип декора: inscription, figurine, topping")
    text: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=30)
    position: str | None = Field(default=None, max_length=30)


class CakeConfigBase(BaseModel):
    dough_id: int | None = Field(default=None, description="ID коржа (для кастомного сбора)")
    preset_id: int | None = Field(default=None, description="ID пресета (для готового торта)")
    decoration: DecorationSchema | None = Field(default=None, description="Декор (JSONB)")


class CakeConfigCreate(CakeConfigBase):
    cake_ingredients: list[CakeIngredientCreate] = Field(
        default_factory=list,
        description="Список кастомных ингредиентов (игнорируется, если передан preset_id)",
    )


class CakeConfigUpdate(BaseModel):
    dough_id: int | None = None
    preset_id: int | None = None
    decoration: DecorationSchema | None = None
    cake_ingredients: list[CakeIngredientCreate] | None = None


class CakeConfigResponse(BaseModel):
    id: int
    dough_id: int | None
    preset_id: int | None
    base_price: Decimal
    total_price: Decimal
    decoration: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CakeConfigDetail(CakeConfigResponse):
    dough: IngredientResponse | None = None
    preset: PresetResponse | None = None
    cake_ingredients: list[CakeIngredientDetail] = Field(default_factory=list)
