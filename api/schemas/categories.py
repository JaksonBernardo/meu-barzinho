from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    company_id: int

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryPublic(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryList(BaseModel):
    items: List[CategoryPublic]
    total: int
    limit: int
    offset: int
    search: Optional[str] = None
