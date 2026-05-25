from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.models.order_items import OrderItem
from typing import Sequence


class OrderItemRepository:

    def __init__(self, db: AsyncSession):
        self.__db = db

    async def exists_by_item_id(self, item_id: int) -> bool:
        query = select(OrderItem).where(OrderItem.item_id == item_id).limit(1)
        result = await self.__db.execute(query)
        return result.scalar_one_or_none() is not None

    async def save(self, order_item: OrderItem) -> OrderItem:
        self.__db.add(order_item)
        await self.__db.flush()
        return order_item

    async def get_by_id_and_order(self, order_item_id: int, order_id: int) -> OrderItem | None:
        query = select(OrderItem).where(
            OrderItem.id == order_item_id, 
            OrderItem.order_id == order_id
        )
        result = await self.__db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_order(self, order_id: int) -> Sequence[OrderItem]:
        query = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self.__db.execute(query)
        return result.scalars().all()

    async def delete(self, order_item: OrderItem) -> None:
        await self.__db.delete(order_item)
        await self.__db.flush()
