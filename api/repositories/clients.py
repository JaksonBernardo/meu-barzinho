from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.models import Client
from typing import Sequence


class ClientRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def save(self, client: Client) -> Client:
        self.__db.add(client)
        await self.__db.flush()
        return client

    async def get_by_id(self, client_id: int, company_id: int) -> Client | None:
        query = select(Client).where(
            Client.id == client_id, 
            Client.company_id == company_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_company(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Sequence[Client]:
        query = (
            select(Client)
            .where(Client.company_id == company_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int) -> int:

        query = (
            select(func.count())
            .select_from(Client)
            .where(Client.company_id == company_id)
        )
        result = await self.__db.execute(query)
        
        return result.scalar() or 0

    async def delete(self, client: Client) -> None:
        await self.__db.delete(client)
        await self.__db.flush()
