from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.models import User, Tenant, UserRole
from app.services.tenant_service import TenantService
from app.services.user_service import UserService
from app.core.security import decode_token

security = HTTPBearer()
settings = get_settings()


async def get_current_tenant(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Tenant:
    host = request.headers.get("host", "").split(":")[0].lower()

    if settings.ENV == "local" and host in ("localhost", "127.0.0.1"):
        slug = request.headers.get("x-tenant", "").strip().lower() or settings.TENANT_DEFAULT_SLUG
        tenant = await TenantService.get_by_slug(session, slug)
    else:
        tenant = await TenantService.get_by_domain(session, host)

    if tenant is None or not tenant.is_active:
        raise HTTPException(status_code=404, detail="Tenant not found or inactive")

    return tenant


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await UserService.get_by_id(session, uid, tenant_id=current_tenant.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_tenant_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin access required",
        )
    return current_user


async def get_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required",
        )
    return current_user