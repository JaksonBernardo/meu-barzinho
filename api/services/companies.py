from api.repositories.companies import CompanyRepository
from api.repositories.users import UserRepository
from api.schemas.companies import CompanyCreate
from api.models.companies import Company
from fastapi import HTTPException, status


class CompanyService:

    def __init__(
        self, company_repo: CompanyRepository, user_repo: UserRepository
    ):
        self.__company_repo = company_repo
        self.__user_repo = user_repo

    async def create_company(self, company_data: CompanyCreate) -> Company:

        existing_user = await self.__user_repo.get_by_email(company_data.admin_user.email)

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O e-mail do administrador já está em uso."
            )

        db = self.__company_repo._CompanyRepository__db

        try:

            company_dict = company_data.model_dump(exclude={"admin_user"})
            company = await self.__company_repo.create(company_dict)

            user_dict = company_data.admin_user.model_dump()
            await self.__user_repo.create(user_dict, company.id)

            await db.commit()
            await db.refresh(company)
            
            return company

        except Exception as e:

            await db.rollback()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar empresa e usuário: {str(e)}"
            )
