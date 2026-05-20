from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.core.database import get_session
from api.repositories.clients import ClientRepository
from api.services.clients import ClientService
from api.schemas.clients import ClientCreate, ClientUpdate, ClientPublic, ClientList
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


def get_client_repository(db: AsyncSession = Depends(get_session)) -> ClientRepository:
    return ClientRepository(db)


def get_client_service(
    client_repo: ClientRepository = Depends(get_client_repository)
) -> ClientService:
    return ClientService(client_repo)


@router.post(
    path="/", 
    response_model=ClientPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_client(
    client_data: ClientCreate,
    client_service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_user)
):
    # Ensure the company_id in client_data matches the user's company
    if client_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar um cliente para esta empresa."
        )
    
    return await client_service.create_client(client_data)


@router.get(
    path="/", 
    response_model=ClientList
)
async def list_clients(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    client_service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_user)
):
    return await client_service.list_clients(current_user.company_id, limit, offset)


@router.get(
    path="/{client_id}", 
    response_model=ClientPublic
)
async def get_client(
    client_id: int,
    client_service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_user)
):
    return await client_service.get_client(client_id, current_user.company_id)


@router.patch(
    path="/{client_id}", 
    response_model=ClientPublic
)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    client_service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_user)
):
    return await client_service.update_client(client_id, current_user.company_id, client_data)


@router.delete(
    path="/{client_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_client(
    client_id: int,
    client_service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_user)
):
    await client_service.delete_client(client_id, current_user.company_id)

    return None
