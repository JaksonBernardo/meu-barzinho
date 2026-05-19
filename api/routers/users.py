from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.core.database import get_session
from api.repositories.users import UserRepository
from api.repositories.companies import CompanyRepository
from api.services.users import UserService
from api.schemas.users import UserCreate, UserPublic
from api.secutiry.jwt import decode_access_token
from api.models.users import User

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)


def get_company_repository(db: AsyncSession = Depends(get_session)) -> CompanyRepository:
    return CompanyRepository(db)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    company_repo: CompanyRepository = Depends(get_company_repository)
) -> UserService:
    return UserService(user_repo, company_repo)


async def get_current_user(
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    user_id = decode_access_token(token)

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    user = await user_repo.get_by_id(user_id)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    return user


@router.post(
    path="/", 
    response_model=UserPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    
    return await user_service.create_user(user_data)
