from pydantic import BaseModel, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List, Literal
from decimal import Decimal

class StockMovement(BaseModel):
    id: int
    type: Literal["ENTRY", "EXIT"]
    item_id: int
    item_name: str
    price: Decimal
    qtd: int
    date: date
    hour: time
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StockReport(BaseModel):
    items: List[StockMovement]
    total: int
    limit: int
    offset: int
