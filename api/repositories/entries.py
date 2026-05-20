from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models.entries import Entry
from typing import Sequence


class EntryRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, entry: Entry) -> Entry:
        self.__db.add(entry)
        await self.__db.flush()
        return entry

    async def get_by_id(self, entry_id: int, company_id: int) -> Entry | None:
        query = select(Entry).where(
            Entry.id == entry_id, 
            Entry.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Entry]:
        query = (
            select(Entry)
            .where(Entry.company_id == company_id)
            .order_by(Entry.date_entry.desc(), Entry.hour.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Entry)
            .where(Entry.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0
