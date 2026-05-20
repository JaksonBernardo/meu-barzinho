from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date, time
from typing import Optional, List
from decimal import Decimal
import uuid

class EntryBase(BaseModel):
    item_id: int
    price: Decimal = Field(ge=0)
    qtd: int = Field(gt=0)
    date_entry: date
    hour: time
    company_id: int

class EntryCreate(EntryBase):
    pass

class EntryPublic(EntryBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EntryList(BaseModel):
    items: List[EntryPublic]
    total: int
    limit: int
    offset: int
