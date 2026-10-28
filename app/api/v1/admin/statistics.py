from datetime import date

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.database import get_session
from app.models import User
from app.schemas import PopularIngredientItem, DailySalesResponse, SuccessResponse, PopularIngredientsResponse, \
    RevenueResponse, FrequentCustomersResponse, PaginatedResponse, OrderResponse
from app.services.statistics_service import StatisticsService

router = APIRouter(
    prefix="/statistics",
    tags=["Admin: Statistics"]
)


@router.get(
    "/daily",
    summary="Продажи по дням",
    response_model=SuccessResponse[DailySalesResponse]
)
async def get_daily_statistics(
        start_date: date,
        end_date: date,
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be less than end date")

    items, total_revenue, total_orders = await StatisticsService.get_daily_sales(session, start_date, end_date)

    return {
        "success": True,
        "data": {
            "items": items,
            "total_revenue": total_revenue,
            "total_orders": total_orders,
        },
    }


@router.get(
    "/popular-ingredients",
    summary="Популярные ингредиенты",
    response_model=SuccessResponse[PopularIngredientsResponse]
)
async def get_popular_ingredients(
        limit: int = Query(10, ge=1, le=50),
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)
):
    popular_ingredients = await StatisticsService.get_popular_ingredients(session=session, limit=limit)

    return {
        "success": True,
        "data": {
            "items": popular_ingredients,
        },
    }


@router.get(
    "/revenue",
    summary="Статистика по выручке",
    response_model=SuccessResponse[RevenueResponse]
)
async def get_revenue_statistics(
        start_date: date,
        end_date: date,
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    total_revenue, avg_order_value, orders_count = await StatisticsService.get_revenue(
        session=session,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "success": True,
        "data": {
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "orders_count": orders_count
        },
    }


@router.get(
    "/frequent-customers",
    summary="Частые клиенты",
    response_model=SuccessResponse[FrequentCustomersResponse]
)
async def get_frequent_customers(
        limit: int = Query(10, ge=1, le=50),
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)

):
    frequent_customers = await StatisticsService.get_frequent_customers(session=session, limit=limit)

    return {
        "success": True,
        "data": {
            "items": frequent_customers,
        },
    }


@router.get(
    "/cancelled",
    summary="cancelled",
    response_model=PaginatedResponse[OrderResponse]
)
async def get_cancelled_statistics(
        page: int = 1,
        limit: int = Query(10, ge=1, le=50),
        session: AsyncSession = Depends(get_session),
        current_admin: User = Depends(get_current_admin)
):
    items, total = await StatisticsService.get_cancelled_orders(session=session, page=page, limit=limit)

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
