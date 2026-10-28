from app.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse,
)

from app.schemas.preset import (
    PresetCreate,
    PresetUpdate,
    PresetResponse,
    PresetDetail,
    PresetIngredientCreate,
    PresetIngredientDetail,
)

from app.schemas.response import SuccessResponse
from app.schemas.pagination import PaginatedResponse, PaginationMeta

from app.schemas.user import UserBase, UserCreate, UserResponse, UserLogin, TokenResponse

from app.schemas.cake_config import (
    CakeConfigCreate,
    CakeConfigUpdate,
    CakeConfigResponse,
    CakeConfigDetail,
    CakeIngredientCreate,
    CakeIngredientDetail,
    DecorationSchema,
)

from app.schemas.order import (
    OrderStatusLogResponse,
    OrderCreate,
    OrderResponse,
    OrderDetail,
    OrderStatusUpdate
)

from app.schemas.statistics import (
    DailySalesItem,
    DailySalesResponse,
    PopularIngredientItem,
    PopularIngredientsResponse,
    RevenueResponse,
    FrequentCustomerItem,
    FrequentCustomersResponse,
    CancelledOrdersResponse,
)

__all__ = [
    # Ingredient
    "IngredientCreate",
    "IngredientUpdate",
    "IngredientResponse",
    # Preset
    "PresetCreate",
    "PresetUpdate",
    "PresetResponse",
    "PresetDetail",
    "PresetIngredientCreate",
    "PresetIngredientDetail",
    # Common
    "SuccessResponse",
    "PaginatedResponse",
    "PaginationMeta",
    #     User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    # CakeConfig
    "CakeConfigCreate",
    "CakeConfigUpdate",
    "CakeConfigResponse",
    "CakeConfigDetail",
    "CakeIngredientCreate",
    "CakeIngredientDetail",
    "DecorationSchema",
    # Orders
    "OrderStatusLogResponse",
    "OrderCreate",
    "OrderResponse",
    "OrderDetail",
    "OrderStatusUpdate",
    # Statistics
    "DailySalesItem",
    "DailySalesResponse",
    "PopularIngredientItem",
    "PopularIngredientsResponse",
    "RevenueResponse",
    "FrequentCustomerItem",
    "FrequentCustomersResponse",
    "CancelledOrdersResponse",
]
