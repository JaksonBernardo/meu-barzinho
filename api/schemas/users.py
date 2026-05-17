from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBaseSchema(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    company_id: int


class UserCreateSchema(UserBaseSchema):
    password: str


class UserResponseSchema(UserBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
