from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import List

class SaleBase(BaseModel):
    order_description: str | None = None
    order_number: int
    item_name: str
    item_id: int
    qtd: int
    item_price: Decimal
    total_value: Decimal
    payment_form: str
    company_id: int

class SaleCreate(SaleBase):
    pass

class SalePublic(SaleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SaleList(BaseModel):
    items: List[SalePublic]
    total: int
    limit: int
    offset: int
