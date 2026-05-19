from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.companies import CompanyRepository
from api.repositories.users import UserRepository
from api.services.companies import CompanyService
from api.schemas.companies import CompanyCreate, CompanyPublic
from api.schemas.users import UserCreateWithCompany, UserPublic
from api.secutiry.jwt import decode_access_token
from api.models.users import User


router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])


def get_company_repository(db: AsyncSession = Depends(get_session)) -> CompanyRepository:
    return CompanyRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)


def get_company_service(
    company_repo: CompanyRepository = Depends(get_company_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> CompanyService:
    
    return CompanyService(company_repo, user_repo)


@router.post(
    path="/", 
    response_model=CompanyPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_company(
    company_data: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service)
):
    
    return await company_service.create_company(company_data)
