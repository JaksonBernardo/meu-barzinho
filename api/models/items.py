from typing import TYPE_CHECKING, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    String, 
    Integer, 
    ForeignKey, 
    DateTime, 
    Numeric, 
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models import Base

if TYPE_CHECKING:
    from api.models.categories import Category
    from api.models.companies import Company


class Item(Base):

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete = "RESTRICT")
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable = False
    )
    stock: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
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

    category: Mapped["Category"] = relationship(back_populates="items")
    company: Mapped["Company"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint(
            "stock > 0",
            name = "check_stock_positive_value"
        ),
        CheckConstraint(
            "price > 0",
            name = "check_price_positive_value"
        )
    )
