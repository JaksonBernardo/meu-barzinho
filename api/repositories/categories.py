from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models.categories import Category
from typing import Sequence


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, category: Category) -> Category:
        self.__db.add(category)
        await self.__db.flush()
        return category

    async def get_by_id(self, category_id: int, company_id: int) -> Category | None:
        query = select(Category).where(
            Category.id == category_id, 
            Category.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Category]:
        query = (
            select(Category)
            .where(Category.company_id == company_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Category)
            .where(Category.company_id == company_id)
        )
        result = await self.__db.execute(query)
        return result.scalar() or 0

    async def delete(self, category: Category) -> None:
        await self.__db.delete(category)
        await self.__db.flush()
