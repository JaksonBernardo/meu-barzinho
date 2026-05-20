from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    String, 
    Text,
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
    from api.models.items import Item
    from api.models.companies import Company


class Sale(Base):

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    
    order_description: Mapped[str] = mapped_column(Text, nullable = True)
    order_number: Mapped[int] = mapped_column(Integer, nullable = False)
    
    item_name: Mapped[str] = mapped_column(String(255), nullable = False)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete = "RESTRICT"),
        nullable = False
    )

    qtd: Mapped[int] = mapped_column(Integer, nullable = False)
    item_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable = False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable = False)
    
    payment_form: Mapped[str] = mapped_column(String(30), nullable = False)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete = "CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now()
    )

    # Relationships
    item: Mapped["Item"] = relationship(back_populates="sales")
    company: Mapped["Company"] = relationship(back_populates="sales")

    __table_args__ = (
        CheckConstraint(
            "qtd > 0",
            name = "chk_sales_qtd"
        ),
        CheckConstraint(
            "item_price >= 0",
            name = "chk_sales_item_price"
        ),
        CheckConstraint(
            "total_value >= 0",
            name = "chk_sales_total_value"
        ),
        CheckConstraint(
            "payment_form IN ('CASH', 'PIX', 'DEBIT', 'CREDIT')",
            name = "chk_sales_payment_form"
        ),
    )
