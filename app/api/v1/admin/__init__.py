from fastapi import APIRouter

from app.api.v1.admin.statistics import router as statistics_router

admin_router = APIRouter(
    prefix="/admin",
)

admin_router.include_router(statistics_router)