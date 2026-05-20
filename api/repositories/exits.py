from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models.exits import Exit
from typing import Sequence


class ExitRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, exit_obj: Exit) -> Exit:
        self.__db.add(exit_obj)
        await self.__db.flush()
        return exit_obj

    async def get_by_id(self, exit_id: int, company_id: int) -> Exit | None:
        query = select(Exit).where(
            Exit.id == exit_id, 
            Exit.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Exit]:
        query = (
            select(Exit)
            .where(Exit.company_id == company_id)
            .order_by(Exit.date_exit.desc(), Exit.hour.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Exit)
            .where(Exit.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0
