from typing import TYPE_CHECKING, List
from enum import Enum
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    String, 
    Text, 
    ForeignKey, 
    DateTime, 
    Numeric, 
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models import Base

if TYPE_CHECKING:
    from api.models.companies import Company
    from api.models.order_items import OrderItem


class StatusOrder(str, Enum):
    OPEN = "ABERTO"
    PAID = "PAGO"
    CANCELED = "CANCELADO"


class TypeDiscount(str, Enum):
    FIXED = "FIXO"
    PERCENT = "PERCENTUAL"


class PaymentForm(str, Enum):
    CASH = "DINHEIRO"
    PIX = "PIX"
    DEBIT = "DEBITO"
    CREDIT = "CREDITO"


class Order(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    number: Mapped[int]
    description: Mapped[str] = mapped_column(Text, nullable = True)
    status: Mapped[StatusOrder] = mapped_column(
        String(20), 
        nullable = False, 
        default = StatusOrder.OPEN
    )
    type_discount: Mapped[TypeDiscount] = mapped_column(
        String(25),
        nullable = False,
        default = TypeDiscount.FIXED
    )
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default = "0.00")
    payment_form: Mapped[PaymentForm] = mapped_column(String(30))
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete = "CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now(),
        onupdate = func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")

    __table_args__ = (
        CheckConstraint(
            "discount >= 0",
            name = "check_discount_positive_value"
        ),
        CheckConstraint(
            "status IN ('ABERTO', 'PAGO', 'CANCELADO')",
            name = "check_order_status"
        ),
        CheckConstraint(
            "type_discount IN ('FIXO', 'PERCENTUAL')",
            name = "check_order_type_discount"
        ),
        CheckConstraint(
            "payment_form IN ('DINHEIRO', 'PIX', 'DEBITO', 'CREDITO')",
            name = "check_order_payment_form"
        ),
    )
