from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from api.models import Client
from typing import Sequence
from typing import Optional


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
        offset: int = 0,
        search: Optional[str] = None
    ) -> Sequence[Client]:
        query = select(Client).where(Client.company_id == company_id)
        
        if search:
            query = query.where(
                or_(
                    Client.name.ilike(f"%{search}%"),
                    Client.document.ilike(f"%{search}%")
                )
            )
            
        query = query.limit(limit).offset(offset)
        
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def count_by_company(self, company_id: int, search: Optional[str] = None) -> int:

        query = (
            select(func.count())
            .select_from(Client)
            .where(Client.company_id == company_id)
        )
        
        if search:
            query = query.where(
                or_(
                    Client.name.ilike(f"%{search}%"),
                    Client.document.ilike(f"%{search}%")
                )
            )

        result = await self.__db.execute(query)
        
        return result.scalar() or 0

    async def delete(self, client: Client) -> None:
        await self.__db.delete(client)
        await self.__db.flush()
    async def get_by_email(self, email: str, company_id: int) -> Client | None:
        query = select(Client).where(Client.email == email, Client.company_id == company_id)
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_document(self, document: str, company_id: int) -> Client | None:
        query = select(Client).where(Client.document == document, Client.company_id == company_id)
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()
