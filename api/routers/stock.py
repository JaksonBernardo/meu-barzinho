from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from api.core.database import get_session
from api.repositories.entries import EntryRepository
from api.repositories.exits import ExitRepository
from api.repositories.items import ItemRepository
from api.schemas.stock import StockReport
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/stock/report", tags=["Stock Report"])

@router.get("/", response_model=StockReport)
async def get_stock_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    entry_repo = EntryRepository(db)
    exit_repo = ExitRepository(db)
    item_repo = ItemRepository(db)
    
    # Simple aggregation for now
    # Note: In production, consider a database-level view or union query
    entries = await entry_repo.get_all_by_company(current_user.company_id, limit=100)
    exits = await exit_repo.get_all_by_company(current_user.company_id, limit=100)
    
    movements = []
    for e in entries:
        item = await item_repo.get_by_id(e.item_id, current_user.company_id)
        movements.append({
            "id": e.id,
            "type": "ENTRY",
            "item_id": e.item_id,
            "item_name": item.name if item else "Desconhecido",
            "price": e.price,
            "qtd": e.qtd,
            "date": e.date_entry,
            "hour": e.hour,
            "created_at": e.created_at
        })
        
    for ex in exits:
        item = await item_repo.get_by_id(ex.item_id, current_user.company_id)
        movements.append({
            "id": ex.id,
            "type": "EXIT",
            "item_id": ex.item_id,
            "item_name": item.name if item else "Desconhecido",
            "price": ex.price,
            "qtd": ex.qtd,
            "date": ex.date_exit,
            "hour": ex.hour,
            "created_at": ex.created_at
        })
        
    # Sort and filter by date
    movements.sort(key=lambda x: x["date"], reverse=True)
    
    if start_date:
        movements = [m for m in movements if m["date"] >= start_date]
    if end_date:
        movements = [m for m in movements if m["date"] <= end_date]
        
    return {
        "items": movements,
        "total": len(movements),
        "limit": 100,
        "offset": 0
    }
