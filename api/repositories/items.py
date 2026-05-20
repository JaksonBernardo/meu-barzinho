from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models.items import Item
from typing import Sequence


class ItemRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, item: Item) -> Item:
        self.__db.add(item)
        await self.__db.flush()
        return item

    async def get_by_id(self, item_id: int, company_id: int) -> Item | None:
        query = select(Item).where(
            Item.id == item_id, 
            Item.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Item]:
        query = (
            select(Item)
            .where(Item.company_id == company_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Item)
            .where(Item.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0

    async def delete(self, item: Item) -> None:
        await self.__db.delete(item)
        await self.__db.flush()
