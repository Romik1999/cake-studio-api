from datetime import date

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.api.deps as deps
from app.database import get_session
from app.models import User, StatusEnum
from app.schemas import OrderCreate, SuccessResponse, OrderDetail, PaginatedResponse, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "",
    summary="Создать заказ",
    status_code=201,
    response_model=SuccessResponse[OrderDetail]
)
async def create_order(
        data: OrderCreate,
        session: AsyncSession = Depends(get_session)
):
    try:
        new_order = await OrderService.create(session, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await session.commit()

    return {
        "success": True,
        "data": new_order,
    }


@router.get(
    "",
    summary="Получить список заказов с пагинацией",
    response_model=PaginatedResponse[OrderResponse]
)
async def get_all_orders(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
        status_filter: StatusEnum | None = Query(None, description="Фильтр по статусу"),
        date_filter: date | None = Query(None, description="Фильтр по дате"),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(deps.get_current_user),
):
    if current_user.is_admin:
        items, total = await OrderService.get_all(
            session,
            page=page,
            limit=limit,
            status_filter=status_filter,
            date_filter=date_filter,
        )
    else:
        items, total = await OrderService.get_user_orders(
            session,
            user_id=current_user.id,
            page=page,
            limit=limit,
            status_filter=status_filter,
            date_filter=date_filter,
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
    "/{order_id}",
    summary="Получить заказ по его айди",
    response_model=SuccessResponse[OrderDetail]
)
async def get_order_by_id(
        order_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(deps.get_current_user)
):
    current_order = await OrderService.get_by_id(session, order_id)
    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if not current_user.is_admin and current_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "success": True,
        "data": current_order,
    }


@router.patch(
    "/{order_id}/status",
    summary="Обновить статус заказа",
    response_model=SuccessResponse[OrderDetail]
)
async def update_order(
        order_id: int,
        data: OrderStatusUpdate,
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(deps.get_current_admin)
):
    try:
        current_order = await OrderService.update_order(
            session=session,
            order_id=order_id,
            new_status=data.status,
            changed_by_id=current_admin.id,
            comment=data.comment
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    await session.commit()

    return {
        "success": True,
        "data": current_order,
    }


@router.patch(
    "/{order_id}/cancel",
    summary="Отменить заказ",
    response_model=SuccessResponse[OrderDetail]
)
async def cancel_order(
        order_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(deps.get_current_user)
):
    current_order = await OrderService.get_by_id(session, order_id)
    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if not current_user.is_admin and current_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        cancelled_order = await OrderService.cancel(
            session=session,
            order_id=order_id,
            changed_by_id=current_user.id,
            comment="Canceled by user"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await session.commit()

    return {
        "success": True,
        "data": cancelled_order,
    }
