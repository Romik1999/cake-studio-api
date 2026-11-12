from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserRole
from app.schemas import UserCreate


class UserService:
    @staticmethod
    async def get_by_phone(session: AsyncSession, phone: str, tenant_id: int) -> User | None:
        query = select(User).where(User.phone == phone, User.tenant_id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int, tenant_id: int) -> User | None:
        query = select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: UserCreate, tenant_id: int, role: UserRole = UserRole.CUSTOMER) -> User:
        user_data = data.model_dump(exclude={"password"})
        password_hash = get_password_hash(data.password)
        new_user = User(**user_data, password_hash=password_hash, tenant_id=tenant_id, role=role)
        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate(session: AsyncSession, phone: str, password: str, tenant_id: int) -> User | None:
        current_user = await UserService.get_by_phone(session, phone, tenant_id)
        if not current_user:
            return None
        if not current_user.password_hash:
            return None
        if not verify_password(password, current_user.password_hash):
            return None
        return current_user
