from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_tenant
from app.core.security import create_access_token
from app.database import get_session
from app.models import User, Tenant, UserRole
from app.schemas import UserResponse, UserCreate, UserLogin, SuccessResponse, TokenResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", summary="Регистрация", response_model=SuccessResponse[UserResponse], status_code=201)
async def register_user(
        data: UserCreate,
        session: AsyncSession = Depends(get_session),
        current_tenant: Tenant = Depends(get_current_tenant)
):
    existing_user = await UserService.get_by_phone(session, data.phone, current_tenant.id)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that phone already exists"
        )

    registered_user = await UserService.create(session, data, tenant_id=current_tenant.id, role=UserRole.CUSTOMER)
    await session.commit()

    return {
        "success": True,
        "data": registered_user
    }


@router.post("/login", summary="Авторизация", response_model=SuccessResponse[TokenResponse], status_code=200)
async def login_user(
        data: UserLogin,
        session: AsyncSession = Depends(get_session),
        current_tenant: Tenant = Depends(get_current_tenant)
):
    authorized_user = await UserService.authenticate(session, data.phone, data.password, tenant_id=current_tenant.id)
    if authorized_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({"sub": str(authorized_user.id)})

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "tenant_slug": current_tenant.slug,
            "role": authorized_user.role
        }
    }


@router.get("/me", summary="Получить текущего пользователя", response_model=SuccessResponse[UserResponse],
            status_code=200)
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": current_user
    }
