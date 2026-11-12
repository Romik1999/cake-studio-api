from pydantic import BaseModel, Field, ConfigDict


class TenantBase(BaseModel):
    pass


class TenantResponse(TenantBase):
    id: int
    slug: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=3, max_length=100)
    domain: str = Field(min_length=3, max_length=255)
    is_active: bool = True
    branding: dict | None
    model_config = ConfigDict(from_attributes=True)
