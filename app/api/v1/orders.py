from datetime import date

from fastapi import APIRouter, Query, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_tenant, get_tenant_admin
from app.database import get_session
from app.models import User, StatusEnum, Tenant, UserRole
from app.schemas import (
    OrderCreate,
    SuccessResponse,
    OrderDetail,
    PaginatedResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService
from app.services.telegram_service import TelegramService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    path="",
    summary="Создать заказ",
    status_code=201,
    response_model=SuccessResponse[OrderDetail],
)
async def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    try:
        new_order = await OrderService.create(
            session, data, tenant_id=current_tenant.id
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    background_tasks.add_task(
        TelegramService.notify_new_order,
        new_order.id,
        new_order.tenant_id,
        float(new_order.total_price),
        new_order.delivery_address or "Самовывоз",
    )

    return {
        "success": True,
        "data": new_order,
    }


@router.get(
    path="",
    summary="Получить список заказов с пагинацией и фильтрами",
    response_model=PaginatedResponse[OrderResponse],
)
async def get_all_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    status: list[StatusEnum] | None = Query(
        None, description="Фильтр по статусам (мультивыбор)"
    ),
    created_from: date | None = Query(None, description="Дата создания (от)"),
    created_to: date | None = Query(None, description="Дата создания (до)"),
    search: str | None = Query(
        None, description="Поиск по имени, телефону или ID заказа"
    ),
    sort_by: str | None = Query(None, description="Поле для сортировки"),
    sort_order: str | None = Query(
        None, description="Направление сортировки (asc/desc)"
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    if current_user.role == UserRole.ADMIN:
        items, total = await OrderService.get_all(
            session,
            tenant_id=current_tenant.id,
            page=page,
            limit=limit,
            status=status,
            created_from=created_from,
            created_to=created_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    else:
        items, total = await OrderService.get_user_orders(
            session,
            user_id=current_user.id,
            tenant_id=current_tenant.id,
            page=page,
            limit=limit,
            status=status,
            created_from=created_from,
            created_to=created_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
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
    path="/{order_id}",
    summary="Получить заказ по его айди",
    response_model=SuccessResponse[OrderDetail],
)
async def get_order_by_id(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    current_order = await OrderService.get_by_id(
        session, order_id, tenant_id=current_tenant.id
    )
    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != UserRole.ADMIN and current_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "success": True,
        "data": current_order,
    }


@router.patch(
    path="/{order_id}/status",
    summary="Обновить статус заказа",
    response_model=SuccessResponse[OrderDetail],
)
async def update_order(
    order_id: int,
    data: OrderStatusUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    try:
        current_order = await OrderService.update_order(
            session=session,
            order_id=order_id,
            new_status=data.status,
            changed_by_id=current_admin.id,
            tenant_id=current_tenant.id,
            comment=data.comment,
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "success": True,
        "data": current_order,
    }


@router.patch(
    path="/{order_id}/cancel",
    summary="Отменить заказ",
    response_model=SuccessResponse[OrderDetail],
)
async def cancel_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    current_order = await OrderService.get_by_id(
        session, order_id, tenant_id=current_tenant.id
    )
    if current_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != UserRole.ADMIN and current_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        cancelled_order = await OrderService.cancel(
            session=session,
            tenant_id=current_tenant.id,
            order_id=order_id,
            changed_by_id=current_user.id,
            comment="Canceled by user",
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "success": True,
        "data": cancelled_order,
    }
