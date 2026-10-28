from fastapi import APIRouter

from app.api.v1.ingredients import router as ingredients_router
from app.api.v1.presets import router as presets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.orders import router as orders_router
from app.api.v1.admin import admin_router

api_router = APIRouter()

api_router.include_router(ingredients_router)
api_router.include_router(presets_router)
api_router.include_router(auth_router)
api_router.include_router(orders_router)
api_router.include_router(admin_router)
