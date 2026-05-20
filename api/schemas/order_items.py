from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List
from decimal import Decimal

class OrderItemBase(BaseModel):
    order_id: int
    item_id: int
    price: Decimal = Field(ge=0)
    qtd: int = Field(gt=0)

class OrderItemCreate(BaseModel):
    item_id: int
    price: Decimal = Field(ge=0)
    qtd: int = Field(gt=0)

class OrderItemPublic(OrderItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
