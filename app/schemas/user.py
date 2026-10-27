from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    phone: str = Field(min_length=10, max_length=20, pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)


class UserResponse(UserBase):
    id: int
    is_admin: bool = Field(default=False)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
