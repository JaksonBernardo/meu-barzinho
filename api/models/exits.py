from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime, date, time
from sqlalchemy import (
    String, 
    ForeignKey, 
    DateTime, 
    Date,
    Time,
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


class Exit(Base):

    __tablename__ = "exits"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    uuid: Mapped[str] = mapped_column(String(36), nullable = False)
    
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

    date_exit: Mapped[date] = mapped_column(Date, nullable = False)
    hour: Mapped[time] = mapped_column(Time, nullable = False)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete = "RESTRICT"),
        nullable = False
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

    # Relationships
    item: Mapped["Item"] = relationship(back_populates="exits")
    company: Mapped["Company"] = relationship(back_populates="exits")

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name = "chk_exits_price"
        ),
        CheckConstraint(
            "qtd > 0",
            name = "chk_exits_qtd"
        ),
    )
