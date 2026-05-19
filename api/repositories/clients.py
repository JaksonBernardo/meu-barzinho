from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.models import Client


class ClientRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db


    async def save(self, client: Client) -> Client:

        self.__db.add(client)

        await self.__db.flush()

        return client





