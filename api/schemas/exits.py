from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date, time
from typing import Optional, List
from decimal import Decimal
import uuid

class ExitBase(BaseModel):
    item_id: int
    price: Decimal = Field(ge=0)
    qtd: int = Field(gt=0)
    date_exit: date
    hour: time
    company_id: int

class ExitCreate(ExitBase):
    pass

class ExitPublic(ExitBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExitList(BaseModel):
    items: List[ExitPublic]
    total: int
    limit: int
    offset: int
