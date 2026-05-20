from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.items import ItemRepository
from api.repositories.categories import CategoryRepository
from api.schemas.items import ItemCreate, ItemUpdate
from api.models.items import Item


class ItemService:

    def __init__(self, item_repo: ItemRepository, category_repo: CategoryRepository):
        self.__item_repo = item_repo
        self.__category_repo = category_repo

    async def create_item(self, db: AsyncSession, item_data: ItemCreate) -> Item:
        # Check if category belongs to the company
        category = await self.__category_repo.get_by_id(item_data.category_id, item_data.company_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não encontrada ou não pertence a esta empresa."
            )

        item = Item(**item_data.model_dump())
        
        try:
            await self.__item_repo.save(item)
            await db.commit()
            await db.refresh(item)
            return item
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar item: {str(e)}"
            )

    async def get_item(self, item_id: int, company_id: int) -> Item:
        item = await self.__item_repo.get_by_id(item_id, company_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado."
            )
        return item

    async def list_items(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> dict:
        items = await self.__item_repo.get_all_by_company(company_id, limit, offset)
        total = await self.__item_repo.count_by_company(company_id)
        
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def update_item(
        self, 
        db: AsyncSession, 
        item_id: int, 
        company_id: int, 
        item_data: ItemUpdate
    ) -> Item:
        item = await self.get_item(item_id, company_id)
        
        update_data = item_data.model_dump(exclude_unset=True)
        
        if "category_id" in update_data:
            category = await self.__category_repo.get_by_id(update_data["category_id"], company_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria não encontrada ou não pertence a esta empresa."
                )

        for key, value in update_data.items():
            setattr(item, key, value)
            
        try:
            await self.__item_repo.save(item)
            await db.commit()
            await db.refresh(item)
            return item
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar item: {str(e)}"
            )

    async def delete_item(self, db: AsyncSession, item_id: int, company_id: int) -> None:
        item = await self.get_item(item_id, company_id)
        
        try:
            await self.__item_repo.delete(item)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir item: {str(e)}"
            )
