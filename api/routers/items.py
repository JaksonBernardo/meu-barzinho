from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.items import ItemRepository
from api.repositories.categories import CategoryRepository
from api.services.items import ItemService
from api.schemas.items import ItemCreate, ItemUpdate, ItemPublic, ItemList
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/items", tags=["Items"])


def get_item_repository(db: AsyncSession = Depends(get_session)) -> ItemRepository:
    return ItemRepository(db)

def get_category_repository(db: AsyncSession = Depends(get_session)) -> CategoryRepository:
    return CategoryRepository(db)

def get_item_service(
    item_repo: ItemRepository = Depends(get_item_repository),
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> ItemService:
    return ItemService(item_repo, category_repo)


@router.post(
    path="/", 
    response_model=ItemPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_session),
    item_service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
):
    if item_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar um item para esta empresa."
        )
    
    return await item_service.create_item(db, item_data)


@router.get(
    path="/", 
    response_model=ItemList
)
async def list_items(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    item_service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
):
    return await item_service.list_items(current_user.company_id, limit, offset)


@router.get(
    path="/{item_id}", 
    response_model=ItemPublic
)
async def get_item(
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
):
    return await item_service.get_item(item_id, current_user.company_id)


@router.patch(
    path="/{item_id}", 
    response_model=ItemPublic
)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_session),
    item_service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
):
    return await item_service.update_item(
        db, 
        item_id, 
        current_user.company_id, 
        item_data
    )


@router.delete(
    path="/{item_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_session),
    item_service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
):
    await item_service.delete_item(db, item_id, current_user.company_id)
    return None
