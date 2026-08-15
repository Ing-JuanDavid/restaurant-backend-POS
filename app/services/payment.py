from app.database import Session, SessionDep

from app.models.sales import SaleStatus, Payment
from app.services.sales import SalesService, SalesServiceDep
from app.schemas.sale import SaleSummary
from app.schemas.payment import PaymentPublic, PaymentCreate, PaymentUpdate
from fastapi import Depends
from typing import Annotated

from app.utils.exceptions import sale_paid, invalid, not_found, invalid_action
from datetime import datetime


class PaymentService:

    def __init__(self, session: Session, sale_service: SalesService):
        self.session = session
        self.sale_service = sale_service

    def get_payment(self, payment_id: int) -> Payment:
        db_payment = self.session.get(Payment, payment_id)

        if not db_payment:
            raise not_found("payment")

        return db_payment

    def create_payment(self, payment: PaymentCreate) -> SaleSummary:
        db_sale = self.sale_service.get_sale(payment.sale_id)

        if db_sale.status == SaleStatus.PAGADA:
            raise sale_paid()

        paid = sum(p.amount for p in db_sale.payments)

        pending = db_sale.total - paid

        if payment.amount > pending:
            raise invalid("payment amount")

        db_payment = Payment.model_validate(payment)
        db_payment.created_at = datetime.now()
        db_sale.payments.append(db_payment)

        paid, pending = self.sale_service._update_sale_status(db_sale)

        self.session.commit()
        self.session.refresh(db_payment)
        return self.sale_service._to_sale_summary(db_sale, paid, pending)

    def update_payment(self, payment_id: int, payment_upd: PaymentUpdate) -> SaleSummary:
        # find payment and sale
        db_payment = self.get_payment(payment_id)
        db_sale = db_payment.sale

        # if sale was paid, exception
        if db_sale.status == SaleStatus.PAGADA:
            raise invalid_action("update payment")

        payment_data = payment_upd.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        old_amount = db_payment.amount
        new_amount = payment_data.get("amount", old_amount)

        if new_amount <= 0:
            raise invalid("amount")

        # calculate total paid without old payment
        total_paid = sum(p.amount for p in db_sale.payments if
                         p.payment_id != payment_id)

        total_paid += new_amount

        if total_paid > db_sale.total:
            raise invalid("amount")

        db_payment.sqlmodel_update(payment_data)

        total_pending = db_sale.total - total_paid

        # update sale
        db_sale.status = SaleStatus.PAGADA if total_pending == 0 else SaleStatus.PARCIAL

        self.session.commit()
        self.session.refresh(db_payment)
        self.session.refresh(db_sale)
        return self.sale_service._to_sale_summary(db_sale)

    def get_payments_by_sale(self, sale_id: int) -> list[PaymentPublic]:
        db_sale = self.sale_service.get_sale(sale_id)

        return db_sale.payments


def get_payment_service(session: SessionDep, sale_service: SalesServiceDep):
    return PaymentService(session=session, sale_service=sale_service)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
