from fastapi import APIRouter

from app.api.v1.ingredients import router as ingredients_router

api_router = APIRouter()

api_router.include_router(ingredients_router)
