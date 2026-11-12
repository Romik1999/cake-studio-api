from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_current_tenant, get_tenant_admin
from app.database import get_session
from app.models import User, Tenant
from app.schemas import (
    PaginatedResponse,
    CakeConfigResponse,
    SuccessResponse,
    CakeConfigDetail,
    CakeConfigCreate,
    CakeConfigUpdate,
)
from app.services.cake_config_service import CakeConfigService

router = APIRouter(prefix="/cake-configs", tags=["Cake Configs"])


@router.get(
    path="",
    summary="Получить все конфиги тортов",
    response_model=PaginatedResponse[CakeConfigResponse],
)
async def get_cake_configs(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    session: AsyncSession = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    items, total = await CakeConfigService.get_all(
        session,
        tenant_id=current_tenant.id,
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
    path="/{cake_config_id}",
    summary="Получить конфиг торта по айди",
    response_model=SuccessResponse[CakeConfigDetail],
)
async def get_cake_config(
    cake_config_id: int,
    session: AsyncSession = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    current_cake_config = await CakeConfigService.get_by_id(
        session, cake_config_id, tenant_id=current_tenant.id
    )

    if not current_cake_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cake Config not found"
        )

    return {
        "success": True,
        "data": current_cake_config,
    }


@router.post(
    path="",
    status_code=201,
    summary="Создание конфига торта",
    response_model=SuccessResponse[CakeConfigDetail],
)
async def create_cake_config(
    data: CakeConfigCreate,
    session: AsyncSession = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    try:
        new_cake_config = await CakeConfigService.create(
            session, data, tenant_id=current_tenant.id
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "success": True,
        "data": new_cake_config,
    }


@router.patch(
    path="/{cake_config_id}",
    summary="Обновление конфига торта",
    response_model=SuccessResponse[CakeConfigDetail],
)
async def update_cake_config(
    cake_config_id: int,
    data: CakeConfigUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    try:
        current_cake_config = await CakeConfigService.update(
            session, cake_config_id, data, tenant_id=current_tenant.id
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not current_cake_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Конфиг не найден"
        )

    return {
        "success": True,
        "data": current_cake_config,
    }


@router.delete(
    path="/{cake_config_id}",
    summary="Удаление конфига торта",
    response_model=SuccessResponse[dict],
)
async def delete_cake_config(
    cake_config_id: int,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    is_delete = await CakeConfigService.delete(
        session, cake_config_id, tenant_id=current_tenant.id
    )

    if not is_delete:
        raise HTTPException(status_code=404, detail="Конфиг не найден")

    await session.commit()

    return {
        "success": True,
        "data": {"id": cake_config_id},
    }
