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
    from api.models.users import User
    from api.models.categories import Category
    from api.models.items import Item
    from api.models.clients import Client
    from api.models.orders import Order
    from api.models.entries import Entry
    from api.models.exits import Exit
    from api.models.sales import Sale


class TypeDoc(str, Enum):
    PF = "PF"
    PJ = "PJ"


class Company(Base):

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    customer_id: Mapped[str] = mapped_column(String(255), unique = True, nullable = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    document: Mapped[str] = mapped_column(String(30), nullable = True)
    type_doc: Mapped[TypeDoc] = mapped_column(String(4), nullable = False)
    address: Mapped[str] = mapped_column(String(255), nullable = True)
    plan_id: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now(),
        onupdate = func.now()
    )

    users: Mapped[List["User"]] = relationship(back_populates="company")
    categories: Mapped[List["Category"]] = relationship(back_populates="company")
    items: Mapped[List["Item"]] = relationship(back_populates="company")
    clients: Mapped[List["Client"]] = relationship(back_populates="company")
    orders: Mapped[List["Order"]] = relationship(back_populates="company")
    entries: Mapped[List["Entry"]] = relationship(back_populates="company")
    exits: Mapped[List["Exit"]] = relationship(back_populates="company")
    sales: Mapped[List["Sale"]] = relationship(back_populates="company")
