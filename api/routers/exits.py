from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.exits import ExitRepository
from api.repositories.items import ItemRepository
from api.services.exits import ExitService
from api.schemas.exits import ExitCreate, ExitPublic, ExitList
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/stock/exits", tags=["Stock Exits"])


def get_exit_repository(db: AsyncSession = Depends(get_session)) -> ExitRepository:
    return ExitRepository(db)

def get_item_repository(db: AsyncSession = Depends(get_session)) -> ItemRepository:
    return ItemRepository(db)

def get_exit_service(
    exit_repo: ExitRepository = Depends(get_exit_repository),
    item_repo: ItemRepository = Depends(get_item_repository)
) -> ExitService:
    return ExitService(exit_repo, item_repo)


@router.post(
    path="/", 
    response_model=ExitPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_exit(
    exit_data: ExitCreate,
    db: AsyncSession = Depends(get_session),
    exit_service: ExitService = Depends(get_exit_service),
    current_user: User = Depends(get_current_user)
):
    if exit_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar uma saída para esta empresa."
        )
    
    return await exit_service.create_exit(db, exit_data)


@router.get(
    path="/", 
    response_model=ExitList
)
async def list_exits(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    exit_service: ExitService = Depends(get_exit_service),
    current_user: User = Depends(get_current_user)
):
    return await exit_service.list_exits(current_user.company_id, limit, offset)


@router.get(
    path="/{exit_id}", 
    response_model=ExitPublic
)
async def get_exit(
    exit_id: int,
    exit_service: ExitService = Depends(get_exit_service),
    current_user: User = Depends(get_current_user)
):
    return await exit_service.get_exit(exit_id, current_user.company_id)
