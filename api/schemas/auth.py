from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginPublic(BaseModel):
    name: Optional[str]
    email: EmailStr
    company_id: int
    message: str
