import httpx
from sqlalchemy import select
from app.database import async_session_maker
from app.models.telegram import TelegramRecipient
from app.config import get_settings

settings = get_settings()

TELEGRAM_API_BASE = "https://api.telegram.org"
TELEGRAM_API_BASE_FULL = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}"
TELEGRAM_PARSE_MODE = "HTML"

class TelegramService:
    @staticmethod
    async def get_updates() -> list:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{TELEGRAM_API_BASE_FULL}/getUpdates")
            return res.json().get("result", [])

    @staticmethod
    async def send_message(chat_id: str, text: str):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TELEGRAM_API_BASE_FULL}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": f"{TELEGRAM_PARSE_MODE}"},
            )

    @staticmethod
    async def notify_new_order(order_id: int, tenant_id: int, total_price: float, address: str):
        async with async_session_maker() as session:
            recipients_res = await session.execute(
                select(TelegramRecipient).where(
                    TelegramRecipient.tenant_id == tenant_id,
                    TelegramRecipient.is_active == True
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
