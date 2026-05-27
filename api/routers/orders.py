from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.repositories.orders import OrderRepository
from api.repositories.order_items import OrderItemRepository
from api.repositories.items import ItemRepository
from api.repositories.sales import SaleRepository
from api.services.orders import OrderService
from api.schemas.orders import OrderCreate, OrderUpdate, OrderPublic, OrderList, OrderStatusUpdate
from api.schemas.order_items import OrderItemCreate, OrderItemPublic
from api.models.users import User
from api.routers.users import get_current_user

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


def get_order_repository(db: AsyncSession = Depends(get_session)) -> OrderRepository:
    return OrderRepository(db)

def get_order_item_repository(db: AsyncSession = Depends(get_session)) -> OrderItemRepository:
    return OrderItemRepository(db)

def get_item_repository(db: AsyncSession = Depends(get_session)) -> ItemRepository:
    return ItemRepository(db)

def get_sale_repository(db: AsyncSession = Depends(get_session)) -> SaleRepository:
    return SaleRepository(db)

def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    item_repo: ItemRepository = Depends(get_item_repository),
    sale_repo: SaleRepository = Depends(get_sale_repository)
) -> OrderService:
    return OrderService(order_repo, order_item_repo, item_repo, sale_repo)


@router.post(
    path="/", 
    response_model=OrderPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    if order_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar um pedido para esta empresa."
        )
    
    return await order_service.create_order(db, order_data)


@router.get(
    path="/", 
    response_model=OrderList
)
async def list_orders(
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.list_orders(current_user.company_id, limit, offset)


@router.get(
    path="/{order_id}", 
    response_model=OrderPublic
)
async def get_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.get_order(order_id, current_user.company_id)


@router.patch(
    path="/{order_id}", 
    response_model=OrderPublic
)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.update_order(
        db, 
        order_id, 
        current_user.company_id, 
        order_data
    )


@router.patch(
    path="/{order_id}/status", 
    response_model=OrderPublic
)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.update_order_status(
        db, 
        order_id, 
        current_user.company_id, 
        status_data.status,
        payment_form=status_data.payment_form.value if status_data.payment_form else None
    )


@router.delete(
    path="/{order_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    await order_service.delete_order(db, order_id, current_user.company_id)
    return None


# Order Items Management

@router.post(
    path="/{order_id}/items", 
    response_model=OrderItemPublic,
    status_code=status.HTTP_201_CREATED
)
async def add_item_to_order(
    order_id: int,
    item_data: OrderItemCreate,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.add_item_to_order(
        db, 
        order_id, 
        current_user.company_id, 
        item_data
    )


@router.delete(
    path="/{order_id}/items/{order_item_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_item_from_order(
    order_id: int,
    order_item_id: int,
    db: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    await order_service.remove_item_from_order(
        db, 
        order_id, 
        order_item_id, 
        current_user.company_id
    )
    return None
