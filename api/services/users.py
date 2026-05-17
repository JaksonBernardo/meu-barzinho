from fastapi import HTTPException, status
from api.repositories.users import UserRepository
from api.repositories.companies import CompanyRepository
from api.schemas.users import UserCreateSchema
from api.models.users import User


class UserService:

    def __init__(
        self, 
        user_repo: UserRepository, 
        company_repo: CompanyRepository
    ):
        self.__user_repo = user_repo
        self.__company_repo = company_repo

    async def create_user(self, user_data: UserCreateSchema) -> User:

        company = await self.__company_repo.get_by_id(user_data.company_id)

        if not company:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa com ID {user_data.company_id} não encontrada"
            )

        existing_user = await self.__user_repo.get_by_email(user_data.email)

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        return await self.user_repo.create(user_data.model_dump())
