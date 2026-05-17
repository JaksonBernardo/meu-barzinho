from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from api.models.users import User
from api.secutiry.password import hash_password


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def get_by_email(self, email: str) -> User | None:

        query = select(User).where(User.email == email)

        result = await self.__db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:

        query = select(User).where(User.id == user_id)

        result = await self.__db.execute(query)

        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:

        user_data["password"] = hash_password(user_data["password"])

        user = User(**user_data)

        self.__db.add(user)

        await self.__db.commit()
        await self.__db.refresh(user)
        
        return user
