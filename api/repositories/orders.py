from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from api.models.orders import Order
from typing import Sequence


class OrderRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, order: Order) -> Order:
        self.__db.add(order)
        await self.__db.flush()
        return order

    async def get_by_id(self, order_id: int, company_id: int) -> Order | None:
        query = (
            select(Order)
            .options(selectinload(Order.order_items))
            .where(
                Order.id == order_id, 
                Order.company_id == company_id
            )
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Order]:
        query = (
            select(Order)
            .options(selectinload(Order.order_items))
            .where(Order.company_id == company_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Order)
            .where(Order.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0

    async def delete(self, order: Order) -> None:
        await self.__db.delete(order)
        await self.__db.flush()
