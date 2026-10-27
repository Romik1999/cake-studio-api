from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas import UserCreate


class UserService:
    @staticmethod
    async def get_by_phone(session: AsyncSession, phone: str) -> User | None:
        query = select(User).where(User.phone == phone)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: UserCreate) -> User:
        user_data = data.model_dump(exclude={"password"})
        password_hash = get_password_hash(data.password)
        new_user = User(**user_data, password_hash=password_hash)
        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate(session: AsyncSession, phone: str, password: str) -> User | None:
        current_user = await UserService.get_by_phone(session, phone)
        if not current_user:
            return None
        if not current_user.password_hash:
            return None
        if not verify_password(password, current_user.password_hash):
            return None
        return current_user
