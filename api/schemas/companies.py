from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class TypeDoc(str, Enum):
    PF = "PF"
    PJ = "PJ"

class CompanyBase(BaseModel):
    name: str
    document: Optional[str] = None
    type_doc: TypeDoc
    address: Optional[str] = None
    plan_id: int

    @field_validator("document")
    @classmethod
    def sanitize_document(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.replace(".", "").replace("-", "").replace("/", "")
        return v

class CompanyCreate(CompanyBase):
    customer_id: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    customer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
