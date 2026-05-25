from fastapi import HTTPException, status
from api.repositories.clients import ClientRepository
from api.schemas.clients import ClientCreate, ClientUpdate
from api.models import Client
from typing import Sequence, Optional


class ClientService:

    def __init__(self, client_repo: ClientRepository):
        self.__client_repo = client_repo

    async def create_client(self, client_data: ClientCreate) -> Client:
        # Verificar duplicidade
        if client_data.email:
            existing = await self.__client_repo.get_by_email(client_data.email, client_data.company_id)
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado para esta empresa.")

        if client_data.document:
            existing = await self.__client_repo.get_by_document(client_data.document, client_data.company_id)
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Documento já cadastrado para esta empresa.")

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
        offset: int = 0,
        search: Optional[str] = None
    ) -> dict:
        clients = await self.__client_repo.get_all_by_company(company_id, limit, offset, search)
        total = await self.__client_repo.count_by_company(company_id, search)
        
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
