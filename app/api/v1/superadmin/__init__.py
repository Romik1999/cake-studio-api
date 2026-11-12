from fastapi import APIRouter

from app.api.v1.superadmin.tenants import router as tenants_router

superadmin_router = APIRouter(prefix="/superadmin")
superadmin_router.include_router(tenants_router)