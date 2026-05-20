from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from api.models.orders import StatusOrder, TypeDiscount, PaymentForm
from api.schemas.order_items import OrderItemPublic

class OrderBase(BaseModel):
    number: int
    description: Optional[str] = None
    status: StatusOrder = StatusOrder.OPEN
    type_discount: TypeDiscount = TypeDiscount.FIXED
    discount: Decimal = Decimal("0.00")
    payment_form: PaymentForm
    company_id: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[StatusOrder] = None
    type_discount: Optional[TypeDiscount] = None
    discount: Optional[Decimal] = None
    payment_form: Optional[PaymentForm] = None

class OrderStatusUpdate(BaseModel):
    status: StatusOrder

class OrderPublic(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemPublic] = []

    model_config = ConfigDict(from_attributes=True)

class OrderList(BaseModel):
    items: List[OrderPublic]
    total: int
    limit: int
    offset: int
