from api.repositories.companies import CompanyRepository
from api.schemas.companies import CompanyCreate
from api.models.companies import Company


class CompanyService:
    def __init__(self, company_repo: CompanyRepository):
        self.company_repo = company_repo

    async def create_company(self, company_data: CompanyCreate) -> Company:
        # Aqui podem ser adicionadas validações futuras (ex: documento único)
        return await self.company_repo.create(company_data.model_dump())
