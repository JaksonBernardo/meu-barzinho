from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.models.companies import Company


class CompanyRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def get_by_id(self, company_id: int) -> Company | None:

        query = select(Company).where(Company.id == company_id)

        result = await self.__db.execute(query)

        return result.scalar_one_or_none()

    async def create(self, company_data: dict) -> Company:
        company = Company(**company_data)
        self.__db.add(company)
        await self.__db.commit()
        await self.__db.refresh(company)
        return company
