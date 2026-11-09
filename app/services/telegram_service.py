import httpx
from sqlalchemy import select
from app.database import async_session_maker
from app.models.telegram import TelegramRecipient
from app.models.user import User
from app.config import get_settings

settings = get_settings()

class TelegramService:
    @staticmethod
    async def get_updates() -> list:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates")
            return res.json().get("result", [])

    @staticmethod
    async def send_message(chat_id: str, text: str):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            )

    @staticmethod
    async def notify_new_order(order_id: int, total_price: float, address: str):
        async with async_session_maker() as session:
            # 👇 Ищем админа ВНУТРИ сервиса
            admin_res = await session.execute(select(User).where(User.is_admin == True).limit(1))
            admin = admin_res.scalar_one_or_none()

            if not admin:
                return

            recipients_res = await session.execute(
                select(TelegramRecipient).where(
                    TelegramRecipient.is_active == True,
                    TelegramRecipient.user_id == admin.id
                )
            )
            recipients = recipients_res.scalars().all()

            text = (
                f"🔔 <b>Новый заказ #{order_id}!</b>\n\n"
                f"💰 Сумма: <b>{total_price} ₽</b>\n"
                f"📍 Адрес: {address}"
            )

            for rec in recipients:
                await TelegramService.send_message(rec.chat_id, text)