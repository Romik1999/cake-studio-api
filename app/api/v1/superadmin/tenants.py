from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_superadmin
from app.database import get_session
from app.models import User
from app.schemas import TenantResponse, PaginatedResponse, SuccessResponse
from app.services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["Superadmin: Tenants"])


@router.get(path="", response_model=PaginatedResponse[TenantResponse])
async def get_tenants(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    is_active: bool | None = Query(None, description="Фильтр по активности"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_superadmin),
):
    items, total = await TenantService.get_all(
        session,
        is_active=is_active,
        page=page,
        limit=limit,
    )

    return {
        "success": True,
        "data": items,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        },
    }


@router.get(
    path="/{tenant_id}",
    summary="Получить тенант по его айди",
    response_model=SuccessResponse[TenantResponse],
)
async def get_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_superadmin),
):
    current_tenant = await TenantService.get_by_id(session, tenant_id=tenant_id)

    if not current_tenant:
        raise HTTPException(status_code=404, detail="Тенант не найден")

    return {
        "success": True,
        "data": current_tenant,
    }
