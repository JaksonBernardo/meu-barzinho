from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from datetime import datetime
from typing import Optional
from api.models.companies import TypeDoc

class ClientBase(BaseModel):
    name: str
    type_client: TypeDoc
    document: Optional[str]
    email: EmailStr
    address: Optional[str]
    whatsapp: Optional[str]
    company_id: int

    @field_validator("document")
    @classmethod
    def sanitize_document(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.replace(".", "").replace("-", "").replace("/", "").strip()
        return v
    
class ClientCreate(ClientBase):
    pass

class ClientPublic(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
