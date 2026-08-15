from app.database import Session, SessionDep
from app.models.sales import Sale, SaleStatus
from app.models.order import Order
from app.schemas.sale import SaleCreate, SalePublic, SaleSummary
from datetime import datetime

from sqlmodel import select, desc
from app.utils.exceptions import not_found

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

    def get_sale(self, sale_id: int) -> Sale:
        db_sale = self.session.get(Sale, sale_id)

        if not db_sale:
            raise not_found("sale")

        return db_sale

    def get_summary_sale(self, sale_id: int) -> SaleSummary:
        db_sale = self.get_sale(sale_id)

        paid, pending = self._update_sale_status(db_sale)

        return self._to_sale_summary(db_sale, paid, pending)

    def get_sales(self, sale_status: SaleStatus | None) -> list[SalePublic]:
        statement = select(Sale).order_by(Sale.created_at)

        if sale_status:
            statement = statement.where(Sale.status == sale_status)

        return self.session.exec(statement)

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

    def _update_sale_status(self, sale: Sale) -> tuple[int, int]:
        total_paid = sum(p.amount for p in sale.payments)
        pending = sale.total - total_paid

        if pending == 0:
            sale.status = SaleStatus.PAGADA
        elif total_paid == 0:
            SaleStatus.PARCIAL
        else:
            SaleStatus.PENDIENTE

        return total_paid, pending

    def _to_sale_summary(self, sale: Sale, paid: int, pending: int):
        return SaleSummary(
            sale_id=sale.sale_id,
            order_id=sale.order_id,
            total=sale.total,
            paid=paid,
            pending=pending,
            status=sale.status
        )


def get_sales_service(session: SessionDep):
    return SalesService(session=session)


SalesServiceDep = Annotated[SalesService, Depends(get_sales_service)]
