from typing import TYPE_CHECKING, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    String, 
    ForeignKey, 
    DateTime, 
    Text, 
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models import Base, TypeDoc

if TYPE_CHECKING:
    from api.models.companies import Company


class Client(Base):

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    type_client: Mapped[TypeDoc] = mapped_column(String(4), nullable = True)
    document: Mapped[str] = mapped_column(String(50), nullable = True)
    email: Mapped[str] = mapped_column(String(100), nullable = True)
    address: Mapped[str] = mapped_column(Text, nullable = True)
    whatsapp: Mapped[str] = mapped_column(String(30), nullable = True)
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

    company: Mapped["Company"] = relationship(back_populates="clients")
