from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.entries import EntryRepository
from api.repositories.items import ItemRepository
from api.services.entries import EntryService
from api.schemas.entries import EntryCreate, EntryPublic, EntryList
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/stock/entries", tags=["Stock Entries"])


def get_entry_repository(db: AsyncSession = Depends(get_session)) -> EntryRepository:
    return EntryRepository(db)

def get_item_repository(db: AsyncSession = Depends(get_session)) -> ItemRepository:
    return ItemRepository(db)

def get_entry_service(
    entry_repo: EntryRepository = Depends(get_entry_repository),
    item_repo: ItemRepository = Depends(get_item_repository)
) -> EntryService:
    return EntryService(entry_repo, item_repo)


@router.post(
    path="/", 
    response_model=EntryPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_entry(
    entry_data: EntryCreate,
    db: AsyncSession = Depends(get_session),
    entry_service: EntryService = Depends(get_entry_service),
    current_user: User = Depends(get_current_user)
):
    if entry_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar uma entrada para esta empresa."
        )
    
    return await entry_service.create_entry(db, entry_data)


@router.get(
    path="/", 
    response_model=EntryList
)
async def list_entries(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    entry_service: EntryService = Depends(get_entry_service),
    current_user: User = Depends(get_current_user)
):
    return await entry_service.list_entries(current_user.company_id, limit, offset)


@router.get(
    path="/{entry_id}", 
    response_model=EntryPublic
)
async def get_entry(
    entry_id: int,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: User = Depends(get_current_user)
):
    return await entry_service.get_entry(entry_id, current_user.company_id)
