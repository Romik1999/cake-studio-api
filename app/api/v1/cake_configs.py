from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_current_admin
from app.database import get_session
from app.models import User
from app.schemas import PaginatedResponse, CakeConfigResponse, SuccessResponse, CakeConfigDetail, CakeConfigCreate, \
    CakeConfigUpdate
from app.services.cake_config_service import CakeConfigService

router = APIRouter(
    prefix="/cake-configs",
    tags=["Cake Configs"]
)


@router.get("", summary="Получить все конфиги тортов", response_model=PaginatedResponse[CakeConfigResponse])
async def get_cake_configs(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
        session: AsyncSession = Depends(get_session)
):
    items, total = await CakeConfigService.get_all(
        session,
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


@router.get("/{cake_config_id}", summary="Получить конфиг торта по айди",
            response_model=SuccessResponse[CakeConfigDetail])
async def get_cake_config(cake_config_id: int, session: AsyncSession = Depends(get_session)):
    current_cake_config = await CakeConfigService.get_by_id(session, cake_config_id)

    if not current_cake_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cake Config not found"
        )

    return {
        "success": True,
        "data": current_cake_config,
    }


@router.post("", status_code=201, summary="Создание конфига торта", response_model=SuccessResponse[CakeConfigDetail])
async def create_cake_config(
        data: CakeConfigCreate,
        session: AsyncSession = Depends(get_session),
):
    try:
        new_cake_config = await CakeConfigService.create(session, data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await session.commit()

    return {
        "success": True,
        "data": new_cake_config,
    }


@router.patch("/{cake_config_id}", summary="Обновление конфига торта", response_model=SuccessResponse[CakeConfigDetail])
async def update_cake_config(
        cake_config_id: int,
        data: CakeConfigUpdate,
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)
):
    try:
        current_cake_config = await CakeConfigService.update(session, cake_config_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not current_cake_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Конфиг не найден")

    await session.commit()
    # Убрали refresh

    return {
        "success": True,
        "data": current_cake_config,
    }


@router.delete("/{cake_config_id}", summary="Удаление конфига торта", response_model=SuccessResponse[dict])
async def delete_cake_config(
        cake_config_id: int,
        session: AsyncSession = Depends(get_session),
        admin: User = Depends(get_current_admin)
):
    is_delete = await CakeConfigService.delete(session, cake_config_id)

    if not is_delete:
        raise HTTPException(status_code=404, detail="Конфиг не найден")

    await session.commit()

    return {
        "success": True,
        "data": {
            "id": cake_config_id
        },
    }
