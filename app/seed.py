import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User


async def create_super_admin():
    async with async_session_maker() as session:
        # Проверяем, есть ли уже админ
        query = select(User).where(User.is_admin == True)
        result = await session.execute(query)
        admin = result.scalar_one_or_none()

        if admin:
            print("⚠️  Super admin already exists!")
            return

    admin = User(
        name="Admin",
        phone="+79999999999",
        email="admin@cake-studio.com",
        password_hash="admin",
        is_admin=True
    )

    session.add(admin)
    await session.commit()
    print("✅ Super admin created!")
    print("📱 Phone: +79999999999")
    print("🔑 Password: admin")


if __name__ == "__main__":
    asyncio.run(create_super_admin())
