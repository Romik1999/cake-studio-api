from pydantic import BaseModel


class TelegramSettingsDTO(BaseModel):
    bot_username: str


class TelegramRecipientDTO(BaseModel):
    id: int
    chat_id: str
    name: str
    is_active: bool
    user_id: int


class TelegramSyncDTO(BaseModel):
    added: int