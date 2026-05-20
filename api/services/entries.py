import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.entries import EntryRepository
from api.repositories.items import ItemRepository
from api.schemas.entries import EntryCreate
from api.models.entries import Entry


class EntryService:

    def __init__(self, entry_repo: EntryRepository, item_repo: ItemRepository):
        self.__entry_repo = entry_repo
        self.__item_repo = item_repo

    async def create_entry(self, db: AsyncSession, entry_data: EntryCreate) -> Entry:
        # Check if item belongs to the company
        item = await self.__item_repo.get_by_id(entry_data.item_id, entry_data.company_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item não encontrado ou não pertence a esta empresa."
            )

        # Generate UUID automatically
        entry_dict = entry_data.model_dump()
        entry_dict["uuid"] = str(uuid.uuid4())
        
        entry = Entry(**entry_dict)
        
        try:
            # Save the entry
            await self.__entry_repo.save(entry)
            
            # Update item stock
            item.stock += entry.qtd
            await self.__item_repo.save(item)
            
            await db.commit()
            await db.refresh(entry)
            return entry
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar entrada de estoque: {str(e)}"
            )

    async def get_entry(self, entry_id: int, company_id: int) -> Entry:
        entry = await self.__entry_repo.get_by_id(entry_id, company_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada de estoque não encontrada."
            )
        return entry

    async def list_entries(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> dict:
        entries = await self.__entry_repo.get_all_by_company(company_id, limit, offset)
        total = await self.__entry_repo.count_by_company(company_id)
        
        return {
            "items": entries,
            "total": total,
            "limit": limit,
            "offset": offset
        }
