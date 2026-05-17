from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.companies import CompanyRepository
from api.services.companies import CompanyService
from api.schemas.companies import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])


def get_company_repository(db: AsyncSession = Depends(get_session)) -> CompanyRepository:
    return CompanyRepository(db)


def get_company_service(
    company_repo: CompanyRepository = Depends(get_company_repository)
) -> CompanyService:
    return CompanyService(company_repo)


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service)
):
   
    return await company_service.create_company(company_data)
