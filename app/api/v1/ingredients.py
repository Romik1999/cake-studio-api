from tabnanny import check

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import CategoryEnum
from app.schemas import PaginatedResponse, IngredientResponse, SuccessResponse, IngredientCreate, IngredientUpdate
from app.services.ingredient_service import IngredientService

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"]
)


@router.get("", summary="Получить все ингредиенты", response_model=PaginatedResponse[IngredientResponse])
async def get_ingredients(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
        category: CategoryEnum | None = Query(None, description="Фильтр по категории"),
        is_active: bool | None = Query(None, description="Фильтр по активности"),
        session: AsyncSession = Depends(get_session)
):
    items, total = await IngredientService.get_all(
        session,
        category=category,
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


@router.get("/{ingredient_id}", summary="Получить ингредиент по его айди", response_model=SuccessResponse[IngredientResponse])
async def get_ingredient(ingredient_id: int, session: AsyncSession = Depends(get_session)):
    current_ingredient = await IngredientService.get_by_id(session, ingredient_id)

    if not current_ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")

    return {
        "success": True,
        "data": current_ingredient,
    }


@router.patch("/{ingredient_id}", summary="Обновить поля ингредиента по его айди", response_model=SuccessResponse[IngredientResponse])
async def update_ingredient(ingredient_id: int, data: IngredientUpdate, session: AsyncSession = Depends(get_session)):
    current_ingredient = await IngredientService.update(session, ingredient_id, data)

    if not current_ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")

    return {
        "success": True,
        "data": current_ingredient,
    }


@router.post("", summary="Создать ингредиент",  response_model=SuccessResponse[IngredientResponse], status_code=201)
async def create_ingredient(data: IngredientCreate, session: AsyncSession = Depends(get_session)):
    created_ingredient = await IngredientService.create(session, data)
    await session.commit()
    await session.refresh(created_ingredient)

    return {
        "success": True,
        "data": created_ingredient,
    }


@router.delete("/{ingredient_id}", summary="Удалить ингредиент", response_model=SuccessResponse[dict])
async def delete_ingredient(ingredient_id: int, session: AsyncSession = Depends(get_session)):
    is_delete = await IngredientService.delete(session, ingredient_id)

    if not is_delete:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")

    await session.commit()

    return {
        "success": True,
        "data": {
            "id": ingredient_id
        },
    }
