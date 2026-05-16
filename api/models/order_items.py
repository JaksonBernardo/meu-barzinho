from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    ForeignKey, 
    DateTime, 
    Numeric, 
    Integer,
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models import Base

if TYPE_CHECKING:
    from api.models.orders import Order
    from api.models.items import Item


class OrderItem(Base):

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete = "CASCADE"),
        nullable = False
    )
    
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete = "RESTRICT"),
        nullable = False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), 
        nullable = False
    )
    
    qtd: Mapped[int] = mapped_column(
        Integer, 
        nullable = False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now()
    )

    order: Mapped["Order"] = relationship(back_populates="order_items")
    item: Mapped["Item"] = relationship(back_populates="order_items")

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name = "check_order_item_price"
        ),
        CheckConstraint(
            "qtd > 0",
            name = "check_order_item_qtd"
        ),
    )
