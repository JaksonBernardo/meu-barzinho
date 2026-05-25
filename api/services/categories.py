from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.categories import CategoryRepository
from api.schemas.categories import CategoryCreate, CategoryUpdate
from api.models.categories import Category


class CategoryService:

    def __init__(self, category_repo: CategoryRepository):
        self.__category_repo = category_repo

    async def create_category(self, db: AsyncSession, category_data: CategoryCreate) -> Category:
        category = Category(**category_data.model_dump())
        
        try:
            await self.__category_repo.save(category)
            await db.commit()
            await db.refresh(category)
            return category
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar categoria: {str(e)}"
            )

    async def get_category(self, category_id: int, company_id: int) -> Category:
        category = await self.__category_repo.get_by_id(category_id, company_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada."
            )
        return category

    async def list_categories(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0,
        search: str | None = None
    ) -> dict:
        categories = await self.__category_repo.get_all_by_company(company_id, limit, offset, search)
        total = await self.__category_repo.count_by_company(company_id, search)
        
        return {
            "items": categories,
            "total": total,
            "limit": limit,
            "offset": offset,
            "search": search
        }

    async def update_category(
        self, 
        db: AsyncSession, 
        category_id: int, 
        company_id: int, 
        category_data: CategoryUpdate
    ) -> Category:
        category = await self.get_category(category_id, company_id)
        
        update_data = category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)
            
        try:
            await self.__category_repo.save(category)
            await db.commit()
            await db.refresh(category)
            return category
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar categoria: {str(e)}"
            )

    async def delete_category(self, db: AsyncSession, category_id: int, company_id: int) -> None:
        category = await self.get_category(category_id, company_id)
        
        try:
            await self.__category_repo.delete(category)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir categoria: {str(e)}"
            )
