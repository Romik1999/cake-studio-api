from datetime import date

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_admin, get_current_tenant
from app.database import get_session
from app.models import User, Tenant
from app.schemas import (
    DailySalesResponse,
    SuccessResponse,
    PopularIngredientsResponse,
    RevenueResponse,
    FrequentCustomersResponse,
    PaginatedResponse,
    OrderResponse,
)
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Admin: Statistics"])


@router.get(
    path="/daily",
    summary="Продажи по дням",
    response_model=SuccessResponse[DailySalesResponse],
)
async def get_daily_statistics(
    start_date: date,
    end_date: date,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be less than end date"
        )

    items, total_revenue, total_orders = await StatisticsService.get_daily_sales(
        session, tenant_id=current_tenant.id, start_date=start_date, end_date=end_date
    )

    return {
        "success": True,
        "data": {
            "items": items,
            "total_revenue": total_revenue,
            "total_orders": total_orders,
        },
    }


@router.get(
    path="/popular-ingredients",
    summary="Популярные ингредиенты",
    response_model=SuccessResponse[PopularIngredientsResponse],
)
async def get_popular_ingredients(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    popular_ingredients = await StatisticsService.get_popular_ingredients(
        session=session, tenant_id=current_tenant.id, limit=limit
    )

    return {
        "success": True,
        "data": {
            "items": popular_ingredients,
        },
    }


@router.get(
    path="/revenue",
    summary="Статистика по выручке",
    response_model=SuccessResponse[RevenueResponse],
)
async def get_revenue_statistics(
    start_date: date,
    end_date: date,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="Start date cannot be after end date"
        )

    total_revenue, avg_order_value, orders_count = await StatisticsService.get_revenue(
        session=session,
        tenant_id=current_tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "success": True,
        "data": {
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "orders_count": orders_count,
        },
    }


@router.get(
    path="/frequent-customers",
    summary="Частые клиенты",
    response_model=SuccessResponse[FrequentCustomersResponse],
)
async def get_frequent_customers(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    frequent_customers = await StatisticsService.get_frequent_customers(
        session=session, tenant_id=current_tenant.id, limit=limit
    )

    return {
        "success": True,
        "data": {
            "items": frequent_customers,
        },
    }


@router.get(
    path="/cancelled",
    summary="Отменённые заказы",
    response_model=PaginatedResponse[OrderResponse],
)
async def get_cancelled_statistics(
    page: int = 1,
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    items, total = await StatisticsService.get_cancelled_orders(
        session=session, tenant_id=current_tenant.id, page=page, limit=limit
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
