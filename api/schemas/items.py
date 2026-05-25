from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class ItemBase(BaseModel):
    name: str
    category_id: int
    price: Decimal = Field(gt=0)
    company_id: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)

class ItemPublic(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    stock: int

    model_config = ConfigDict(from_attributes=True)

class ItemList(BaseModel):
    items: List[ItemPublic]
    total: int
    limit: int
    offset: int
    search: Optional[str] = None
