from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from datetime import datetime
from typing import Optional, List
from api.models.companies import TypeDoc

class ClientBase(BaseModel):
    name: str
    type_client: TypeDoc
    document: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    whatsapp: Optional[str] = None
    company_id: int

    @field_validator("document")
    @classmethod
    def sanitize_document(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.replace(".", "").replace("-", "").replace("/", "").strip()
        return v
    
class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    type_client: Optional[TypeDoc] = None
    document: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    whatsapp: Optional[str] = None

    @field_validator("document")
    @classmethod
    def sanitize_document(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.replace(".", "").replace("-", "").replace("/", "").strip()
        return v

class ClientPublic(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClientList(BaseModel):
    items: List[ClientPublic]
    total: int
    limit: int
    offset: int
