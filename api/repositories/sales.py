from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models.sales import Sale
from typing import Sequence


class SaleRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def exists_by_item_id(self, item_id: int) -> bool:
        query = select(Sale).where(Sale.item_id == item_id).limit(1)
        result = await self.__db.execute(query)
        return result.scalar_one_or_none() is not None

    async def save(self, sale: Sale) -> Sale:
        self.__db.add(sale)
        await self.__db.flush()
        return sale

    async def get_by_id(self, sale_id: int, company_id: int) -> Sale | None:
        query = select(Sale).where(
            Sale.id == sale_id,
            Sale.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int,
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Sale]:
        query = (
            select(Sale)
            .where(Sale.company_id == company_id)
            .order_by(Sale.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Sale)
            .where(Sale.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0

    async def delete_by_order(self, order_number: int, company_id: int) -> None:
        from sqlalchemy import delete
        query = delete(Sale).where(
            Sale.order_number == order_number,
            Sale.company_id == company_id
        )
        await self.__db.execute(query)
        await self.__db.flush()
