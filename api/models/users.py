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


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(200), nullable = True)
    email: Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(255), nullable = False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete = "CASCADE")
    )




