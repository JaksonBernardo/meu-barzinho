from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.orders import OrderRepository
from api.repositories.order_items import OrderItemRepository
from api.repositories.items import ItemRepository
from api.repositories.sales import SaleRepository
from api.services.exits import ExitService
from api.schemas.orders import OrderCreate, OrderUpdate
from api.schemas.order_items import OrderItemCreate
from api.schemas.exits import ExitCreate
from api.models.orders import Order, StatusOrder
from api.models.order_items import OrderItem
from api.models.sales import Sale


class OrderService:

    def __init__(
        self, 
        order_repo: OrderRepository, 
        order_item_repo: OrderItemRepository,
        item_repo: ItemRepository,
        sale_repo: SaleRepository = None,
        exit_service: ExitService = None
    ):
        self.__order_repo = order_repo
        self.__order_item_repo = order_item_repo
        self.__item_repo = item_repo
        self.__sale_repo = sale_repo
        self.__exit_service = exit_service

    async def create_order(self, db: AsyncSession, order_data: OrderCreate) -> Order:
        existing_order = await self.__order_repo.get_by_number(order_data.number, order_data.company_id)
        if existing_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um pedido com o número {order_data.number} para esta empresa."
            )

        order = Order(**order_data.model_dump())
        try:
            await self.__order_repo.save(order)
            await db.commit()
            
            # Fetch again to ensure relationships (order_items) are loaded
            return await self.get_order(order.id, order.company_id)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar pedido: {str(e)}"
            )

    async def get_order(self, order_id: int, company_id: int) -> Order:
        order = await self.__order_repo.get_by_id(order_id, company_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        return order

    async def list_orders(
        self, 
        company_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> dict:
        orders = await self.__order_repo.get_all_by_company(company_id, limit, offset)
        total = await self.__order_repo.count_by_company(company_id)
        
        return {
            "items": orders,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def add_item_to_order(
        self, 
        db: AsyncSession, 
        order_id: int, 
        company_id: int, 
        item_data: OrderItemCreate
    ) -> OrderItem:
        order = await self.get_order(order_id, company_id)
        
        if order.status != StatusOrder.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível adicionar itens a um pedido que não está aberto."
            )

        item = await self.__item_repo.get_by_id(item_data.item_id, company_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item não encontrado ou não pertence a esta empresa."
            )

        if item.stock < item_data.qtd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {item.stock}, Solicitado: {item_data.qtd}"
            )

        order_item = OrderItem(
            order_id=order_id,
            item_id=item_data.item_id,
            price=item_data.price,
            qtd=item_data.qtd
        )

        try:
            await self.__order_item_repo.save(order_item)
            
            # Decrement stock
            item.stock -= item_data.qtd
            await self.__item_repo.save(item)
            
            await db.commit()
            await db.refresh(order_item)
            order_item.item = item
            return order_item
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao adicionar item ao pedido: {str(e)}"
            )

    async def remove_item_from_order(
        self, 
        db: AsyncSession, 
        order_id: int, 
        order_item_id: int, 
        company_id: int
    ) -> None:
        order = await self.get_order(order_id, company_id)
        
        if order.status != StatusOrder.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover itens de um pedido que não está aberto."
            )

        order_item = await self.__order_item_repo.get_by_id_and_order(order_item_id, order_id)
        if not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item do pedido não encontrado."
            )

        try:
            # Increment stock back
            item = await self.__item_repo.get_by_id(order_item.item_id, company_id)
            if item:
                item.stock += order_item.qtd
                await self.__item_repo.save(item)
            
            await self.__order_item_repo.delete(order_item)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover item do pedido: {str(e)}"
            )

    async def update_order(
        self, 
        db: AsyncSession, 
        order_id: int, 
        company_id: int, 
        order_data: OrderUpdate
    ) -> Order:
        order = await self.get_order(order_id, company_id)
        
        old_status = order.status
        update_data = order_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(order, key, value)
            
        try:
            await self.__order_repo.save(order)
            
            # If status changed to PAID, create sales records
            if old_status != StatusOrder.PAID and order.status == StatusOrder.PAID:
                await self.__create_sales_from_order(db, order, company_id)
            
            # If status changed FROM PAID to something else, remove sales
            if old_status == StatusOrder.PAID and order.status != StatusOrder.PAID:
                await self.__remove_sales_from_order(order, company_id)

            # If status changed to CANCELLED, return items to stock
            if old_status != StatusOrder.CANCELED and order.status == StatusOrder.CANCELED:
                await self.__restore_stock_from_order(order, company_id)
                
            await db.commit()
            await db.refresh(order)
            return order
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar pedido: {str(e)}"
            )

    async def update_order_status(
        self, 
        db: AsyncSession, 
        order_id: int, 
        company_id: int, 
        new_status: StatusOrder
    ) -> Order:
        order = await self.get_order(order_id, company_id)
        
        old_status = order.status
        if old_status == new_status:
            return order
            
        order.status = new_status
            
        try:
            await self.__order_repo.save(order)
            
            # If status changed to PAID, create sales records
            if old_status != StatusOrder.PAID and order.status == StatusOrder.PAID:
                await self.__create_sales_from_order(db, order, company_id)
            
            # If status changed FROM PAID to something else, remove sales
            if old_status == StatusOrder.PAID and order.status != StatusOrder.PAID:
                await self.__remove_sales_from_order(order, company_id)

            # If status changed to CANCELLED, return items to stock
            if old_status != StatusOrder.CANCELED and order.status == StatusOrder.CANCELED:
                await self.__restore_stock_from_order(order, company_id)
                
            await db.commit()
            await db.refresh(order)
            return order
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar status do pedido: {str(e)}"
            )

    async def __restore_stock_from_order(self, order: Order, company_id: int) -> None:
        items = order.order_items
        for oi in items:
            item = await self.__item_repo.get_by_id(oi.item_id, company_id)
            if item:
                item.stock += oi.qtd
                await self.__item_repo.save(item)

    async def __remove_sales_from_order(self, order: Order, company_id: int) -> None:
        if self.__sale_repo:
            await self.__sale_repo.delete_by_order(order.number, company_id)

    async def __create_sales_from_order(self, db: AsyncSession, order: Order, company_id: int) -> None:
        if not self.__sale_repo:
            return

        from api.models.orders import PaymentForm
        
        items = order.order_items
        
        # Get the payment form name (e.g., 'CASH', 'PIX') to match Sale constraint
        p_form = order.payment_form
        if isinstance(p_form, PaymentForm):
            p_form_name = p_form.name
        else:
            # If it's a string (the value), map it back to the name
            p_form_name = p_form # fallback
            for name, member in PaymentForm.__members__.items():
                if member.value == p_form:
                    p_form_name = name
                    break

        for oi in items:
            item = await self.__item_repo.get_by_id(oi.item_id, company_id)
            item_name = item.name if item else "Item Desconhecido"

            sale = Sale(
                order_description=order.description,
                order_number=order.number,
                item_name=item_name,
                item_id=oi.item_id,
                qtd=oi.qtd,
                item_price=oi.price,
                total_value=oi.price * oi.qtd,
                payment_form=p_form_name,
                company_id=company_id
            )
            await self.__sale_repo.save(sale)
            
            # Create stock exit if exit_service is available
            if self.__exit_service:
                await self.__exit_service.create_exit(db, ExitCreate(
                    item_id=oi.item_id,
                    price=oi.price,
                    qtd=oi.qtd,
                    date_exit=order.created_at.date(),
                    hour=order.created_at.time(),
                    company_id=company_id
                ))

    async def delete_order(self, db: AsyncSession, order_id: int, company_id: int) -> None:
        order = await self.get_order(order_id, company_id)
        
        # When deleting an order, we should probably return the items to stock if it's still OPEN
        if order.status == StatusOrder.OPEN:
            items = await self.__order_item_repo.get_all_by_order(order.id)
            for oi in items:
                item = await self.__item_repo.get_by_id(oi.item_id, company_id)
                if item:
                    item.stock += oi.qtd
                    await self.__item_repo.save(item)

        try:
            await self.__order_repo.delete(order)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir pedido: {str(e)}"
            )
