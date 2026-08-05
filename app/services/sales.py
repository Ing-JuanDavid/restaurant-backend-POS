from app.database import Session, SessionDep
from app.services.order import OrderService, OrderServiceDep
from app.models.sales import Sales
from datetime import datetime

from typing import Annotated
from fastapi import Depends


class SalesService:

    def __init__(self, session: Session, order_service: OrderService):
        self.session = session
        self.order_service = order_service

    def create_sale(self, sale_create):
        order_db = self.order_service.get_order(sale_create.order_id)
        sale_db = Sales.model_validate(sale_create)
        sale_db.total = order_db.total
        sale_db.created_at = datetime.now()


def get_sales_service(session: SessionDep, order_service: OrderServiceDep):
    return SalesService(session=session, order_service=order_service)


SalesServiceDep = Annotated[SalesService, Depends(get_sales_service)]
