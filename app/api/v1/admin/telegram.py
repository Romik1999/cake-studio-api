from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_tenant_admin, get_current_tenant
from app.models import User, Tenant
from app.models.telegram import TelegramRecipient
from app.services.telegram_service import TelegramService
from app.config import get_settings
from app.schemas import (
    SuccessResponse,
    TelegramSettingsDTO,
    TelegramRecipientDTO,
    TelegramSyncDTO,
)

router = APIRouter(prefix="/telegram", tags=["Admin: Telegram"])
settings = get_settings()


@router.get(path="/settings", response_model=SuccessResponse[TelegramSettingsDTO])
async def get_settings_info(
    admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return {"success": True, "data": {"bot_username": settings.TELEGRAM_BOT_USERNAME}}


@router.get(
    path="/recipients", response_model=SuccessResponse[list[TelegramRecipientDTO]]
)
async def get_recipients(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    res = await session.execute(
        select(TelegramRecipient).where(
            TelegramRecipient.tenant_id == current_tenant.id
        )
    )
    return {"success": True, "data": res.scalars().all()}


@router.post(path="/sync", response_model=SuccessResponse[TelegramSyncDTO])
async def sync_recipients(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    updates = await TelegramService.get_updates()
    new_count = 0
    for upd in updates:
        message = upd.get("message")
        if message and "chat" in message:
            chat_id = str(message["chat"]["id"])
            name = message["chat"].get("first_name", "Пользователь")

            exists = await session.execute(
                select(TelegramRecipient).where(
                    TelegramRecipient.tenant_id == current_tenant.id,
                    TelegramRecipient.chat_id == chat_id,
                )
            )
            if not exists.scalar_one_or_none():
                session.add(
                    TelegramRecipient(
                        chat_id=chat_id,
                        name=name,
                        user_id=admin.id,
                        tenant_id=current_tenant.id,
                    )
                )
                new_count += 1

    await session.commit()
    return {"success": True, "data": {"added": new_count}}


@router.post(path="/test", response_model=SuccessResponse[dict])
async def test_message(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_tenant_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    recipients = (
        (
            await session.execute(
                select(TelegramRecipient).where(
                    TelegramRecipient.tenant_id == current_tenant.id
                )
            )
        )
        .scalars()
        .all()
    )

    for rec in recipients:
        await TelegramService.send_message(rec.chat_id, "✅ Тестовое сообщение!")

    return {"success": True, "data": {}}
