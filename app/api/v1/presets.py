from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_session
from app.schemas import (
    PaginatedResponse,
    PresetResponse,
    PresetDetail,
    SuccessResponse,
    PresetCreate,
    PresetUpdate,
)
from app.services.preset_service import PresetService

router = APIRouter(
    prefix="/presets",
    tags=["Presets"],
)


@router.get(
    "",
    summary="Получить все пресеты с пагинацией",
    response_model=PaginatedResponse[PresetResponse],
)
async def get_presets(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
        is_active: bool | None = Query(None, description="Фильтр по активности"),
        session: AsyncSession = Depends(get_session),
):
    items, total = await PresetService.get_all(
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
    "/{preset_id}",
    summary="Получить пресет по его айди",
    response_model=SuccessResponse[PresetDetail],
)
async def get_preset(
        preset_id: int,
        session: AsyncSession = Depends(get_session),
):
    current_preset = await PresetService.get_by_id(session, preset_id)

    if not current_preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пресет не найден",
        )

    return {
        "success": True,
        "data": current_preset,
    }


@router.post(
    "",
    summary="Создать пресет",
    response_model=SuccessResponse[PresetDetail],
    status_code=status.HTTP_201_CREATED,
)
async def create_preset(
        data: PresetCreate,
        session: AsyncSession = Depends(get_session),
):
    created_preset = await PresetService.create(session, data)
    await session.commit()

    return {
        "success": True,
        "data": created_preset,
    }


@router.patch(
    "/{preset_id}",
    summary="Обновить поля пресета по его айди",
    response_model=SuccessResponse[PresetDetail],
)
async def update_preset(
        preset_id: int,
        data: PresetUpdate,
        session: AsyncSession = Depends(get_session),
):
    current_preset = await PresetService.update(session, preset_id, data)

    if not current_preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пресет не найден",
        )

    await session.commit()

    return {
        "success": True,
        "data": current_preset,
    }


@router.delete(
    "/{preset_id}",
    summary="Удалить пресет",
    response_model=SuccessResponse[dict],
)
async def delete_preset(
        preset_id: int,
        session: AsyncSession = Depends(get_session),
):
    is_delete = await PresetService.delete(session, preset_id)

    if not is_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пресет не найден",
        )

    await session.commit()

    return {
        "success": True,
        "data": {"id": preset_id},
    }
