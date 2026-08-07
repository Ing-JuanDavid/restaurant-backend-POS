from app.database import Session, SessionDep
from app.models.sales import Sale
from app.schemas.sale import SaleCreate, SalePublic
from datetime import datetime

from typing import Annotated
from fastapi import Depends


class SalesService:

    def __init__(self, session: Session):
        self.session = session

    # def create_sale(self, sale_create: SaleCreate) -> SalePublic:
    #     order_db = self.order_service.get_order(sale_create.order_id)
    #     sale_db = Sale.model_validate(sale_create)
    #     sale_db.total = order_db.total
    #     sale_db.created_at = datetime.now()

    #     self.session.add(sale_db)
    #     self.session.commit()
    #     self.session.refresh(sale_db)
    #     return sale_db

    def create_sale(self, order: Order) -> Sale:
        db_sale = Sale(
            order_id=order.order_id,
            total=order.total,
            created_at=datetime.now(),
        )

        self.session.add(db_sale)
        self.session.commit()
        self.session.refresh(db_sale)
        return db_sale


def get_sales_service(session: SessionDep):
    return SalesService(session=session)


SalesServiceDep = Annotated[SalesService, Depends(get_sales_service)]
