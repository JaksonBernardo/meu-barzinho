from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.secutiry.password import verify_password
from api.secutiry.jwt import create_access_token
from api.core.settings import Settings
from api.schemas.auth import LoginRequest, LoginResponse
from api.repositories.users import UserRepository

_settings = Settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:

    return UserRepository(db)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    response: Response,
    user_repository: UserRepository = Depends(get_user_repository)
):

    user = await user_repository.get_by_email(login_data.email)

    if not user or not verify_password(user.password, login_data.password):
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    token = create_access_token(
        subject=user.id,
        company_id=user.company_id,
        username=user.name or user.email
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=_settings.JWT_EXPIRATION_MINUTES * 60,
        expires=_settings.JWT_EXPIRATION_MINUTES * 60,
        samesite="lax",
        secure=False,  # Em produção deve ser True (HTTPS)
    )

    return LoginResponse(
        name=user.name,
        email=user.email,
        company_id=user.company_id,
        message="Login realizado com sucesso"
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Logout realizado com sucesso"}
