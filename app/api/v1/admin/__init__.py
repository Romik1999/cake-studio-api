from fastapi import APIRouter

from app.api.v1.admin.statistics import router as statistics_router
from app.api.v1.admin.telegram import router as telegram_router

admin_router = APIRouter(
    prefix="/admin",
)

admin_router.include_router(statistics_router)
admin_router.include_router(telegram_router)