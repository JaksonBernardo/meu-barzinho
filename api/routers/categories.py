from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.categories import CategoryRepository
from api.services.categories import CategoryService
from api.schemas.categories import CategoryCreate, CategoryUpdate, CategoryPublic, CategoryList
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


def get_category_repository(db: AsyncSession = Depends(get_session)) -> CategoryRepository:
    return CategoryRepository(db)


def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    return CategoryService(category_repo)


@router.post(
    path="/", 
    response_model=CategoryPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user)
):
    if category_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar uma categoria para esta empresa."
        )
    
    return await category_service.create_category(db, category_data)


@router.get(
    path="/", 
    response_model=CategoryList
)
async def list_categories(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user)
):
    return await category_service.list_categories(current_user.company_id, limit, offset, search)


@router.get(
    path="/{category_id}", 
    response_model=CategoryPublic
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user)
):
    return await category_service.get_category(category_id, current_user.company_id)


@router.patch(
    path="/{category_id}", 
    response_model=CategoryPublic
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user)
):
    return await category_service.update_category(
        db, 
        category_id, 
        current_user.company_id, 
        category_data
    )


@router.delete(
    path="/{category_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user)
):
    await category_service.delete_category(db, category_id, current_user.company_id)
    return None
