from fastapi import HTTPException, status
from api.repositories.clients import ClientRepository
from api.schemas.clients import ClientCreate, ClientUpdate
from api.models import Client
from typing import Sequence


class ClientService:

    def __init__(self, client_repo: ClientRepository):
        self.__client_repo = client_repo

    async def create_client(self, client_data: ClientCreate) -> Client:
        client = Client(**client_data.model_dump())
        
        try:
            await self.__client_repo.save(client)
            
            db = self.__client_repo._ClientRepository__db
            await db.commit()
            await db.refresh(client)
            return client
        
        except Exception as e:
            
            db = self.__client_repo._ClientRepository__db
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar cliente: {str(e)}"
            )

    async def get_client(self, client_id: int, company_id: int) -> Client:
        client = await self.__client_repo.get_by_id(client_id, company_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )
        return client

    async def list_clients(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> dict:
        clients = await self.__client_repo.get_all_by_company(company_id, limit, offset)
        total = await self.__client_repo.count_by_company(company_id)
        
        return {
            "items": clients,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def update_client(self, client_id: int, company_id: int, client_data: ClientUpdate) -> Client:
        client = await self.get_client(client_id, company_id)
        
        update_data = client_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)
            
        try:
            await self.__client_repo.save(client)
            db = self.__client_repo._ClientRepository__db
            await db.commit()
            await db.refresh(client)
            return client
        except Exception as e:
            db = self.__client_repo._ClientRepository__db
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar cliente: {str(e)}"
            )

    async def delete_client(self, client_id: int, company_id: int) -> None:
        client = await self.get_client(client_id, company_id)
        
        try:
            await self.__client_repo.delete(client)
            db = self.__client_repo._ClientRepository__db
            await db.commit()
        except Exception as e:
            db = self.__client_repo._ClientRepository__db
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir cliente: {str(e)}"
            )
