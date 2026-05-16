from typing import TYPE_CHECKING, List
from enum import Enum
from datetime import datetime
from sqlalchemy import (
    String, 
    Integer, 
    ForeignKey, 
    DateTime, 
    Boolean, 
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models import Base

if TYPE_CHECKING:
    from api.models.companies import Company
    from api.models.items import Item


class Category(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(100), nullable = False)
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

    company: Mapped["Company"] = relationship(back_populates="categories")
    items: Mapped[List["Item"]] = relationship(back_populates="category")
