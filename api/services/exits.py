import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.exits import ExitRepository
from api.repositories.items import ItemRepository
from api.schemas.exits import ExitCreate
from api.models.exits import Exit


class ExitService:

    def __init__(self, exit_repo: ExitRepository, item_repo: ItemRepository):
        self.__exit_repo = exit_repo
        self.__item_repo = item_repo

    async def create_exit(self, db: AsyncSession, exit_data: ExitCreate) -> Exit:
        # Check if item belongs to the company
        item = await self.__item_repo.get_by_id(exit_data.item_id, exit_data.company_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item não encontrado ou não pertence a esta empresa."
            )

        # Validate stock
        if item.stock < exit_data.qtd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Estoque atual: {item.stock}, Saída solicitada: {exit_data.qtd}"
            )

        # Generate UUID automatically
        exit_dict = exit_data.model_dump()
        exit_dict["uuid"] = str(uuid.uuid4())

        exit_obj = Exit(**exit_dict)
        
        try:
            # Save the exit
            await self.__exit_repo.save(exit_obj)
            
            # Update item stock
            item.stock -= exit_obj.qtd
            await self.__item_repo.save(item)
            
            await db.commit()
            await db.refresh(exit_obj)
            return exit_obj
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar saída de estoque: {str(e)}"
            )

    async def get_exit(self, exit_id: int, company_id: int) -> Exit:
        exit_obj = await self.__exit_repo.get_by_id(exit_id, company_id)
        if not exit_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saída de estoque não encontrada."
            )
        return exit_obj

    async def list_exits(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> dict:
        exits = await self.__exit_repo.get_all_by_company(company_id, limit, offset)
        total = await self.__exit_repo.count_by_company(company_id)
        
        return {
            "items": exits,
            "total": total,
            "limit": limit,
            "offset": offset
        }
