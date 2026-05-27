from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from api.core.database import get_session
from api.repositories.sales import SaleRepository
from api.schemas.sales import SalePublic
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])

def get_sale_repository(db: AsyncSession = Depends(get_session)) -> SaleRepository:
    return SaleRepository(db)

@router.get(
    path="/period",
    response_model=List[SalePublic]
)
async def list_sales_by_period(
    start_date: date = Query(...),
    end_date: date = Query(...),
    sale_repo: SaleRepository = Depends(get_sale_repository),
    current_user: User = Depends(get_current_user)
):
    return await sale_repo.get_all_by_company_and_period(
        current_user.company_id,
        start_date,
        end_date
    )
