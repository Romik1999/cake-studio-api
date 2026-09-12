from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int = Field(description="Всего записей в БД")
    page: int = Field(description="Текущая страница")
    limit: int = Field(description="Размер страницы")
    pages: int = Field(description="Всего страниц")


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    meta: PaginationMeta