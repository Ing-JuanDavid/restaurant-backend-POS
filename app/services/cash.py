from app.database import Session, SessionDep
from app.models.cash import CashSession, CashStatus, CashMovement
from app.models.sales import Payment
from typing import Annotated
from fastapi import Depends
from app.models.cash import MovementType
from app.schemas.cash import CashDetailPublic, CashMovementPublic
from datetime import datetime
from sqlmodel import select

from app.utils.exceptions import not_found, invalid_action, opened_cash


class CashSessionService:

    def __init__(self, session: Session):
        self.session = session

    def get_cash(self, cash_id: int) -> CashSession:
        db_cash = self.session.get(CashSession, cash_id)

        if not db_cash:
            raise not_found("cash")

        return db_cash

    def get_cash_details(self, cash_id: int) -> CashDetailPublic:
        db_cash = self.get_cash(cash_id)
        data = self._get_expected_closing_balcance(db_cash)
        return self._to_cash_details(db_cash, data)

    def get_movements(self, cash_id: int) -> list[CashMovementPublic]:
        db_cash = self.get_cash(cash_id)

        return db_cash.movements

    def get_opened_cash(self) -> CashSession | None:
        statement = select(CashSession).where(
            CashSession.status == CashStatus.ABIERTA)
        return self.session.exec(statement).first()

    def open_cash(self, opening_balance: int) -> CashSession:

        is_opened_cash = self.get_opened_cash()

        if is_opened_cash:
            raise opened_cash(is_opened_cash.cash_session_id)

        db_cash = CashSession()
        db_cash.opening_balance = opening_balance
        db_cash.status = CashStatus.ABIERTA
        db_cash.opened_at = datetime.now()
        self.session.add(db_cash)
        self.save_cash(db_cash)
        return db_cash

    def close_cash(self, cash_id: int, closing_balance: int) -> CashDetailPublic:
        db_cash = self.get_cash(cash_id)

        if db_cash.status == CashStatus.CERRADA:
            raise invalid_action("close cash")

        cash_data = self._get_expected_closing_balcance(db_cash)

        db_cash.closing_balance = closing_balance
        db_cash.expec_closing_balance = cash_data[0]
        db_cash.difference = closing_balance - cash_data[0]
        db_cash.status = CashStatus.CERRADA
        db_cash.closed_at = datetime.now()
        self.save_cash(db_cash)

        return self._to_cash_details(db_cash, cash_data)

    def payment_to_cash_movement(self, payment: Payment) -> CashMovement:
        cash_movement = CashMovement(
            amount=payment.amount,
            payment_method=payment.method,
            movement_type=MovementType.INGRESO,
            created_at=datetime.now(),
        )

        return cash_movement

    def save_cash(self, cash: CashSession):
        self.session.commit()
        self.session.refresh(cash)

    def _get_expected_closing_balcance(self, cash: CashSession) -> tuple[int, int, int, int]:
        expect_balance = 0
        cash_total, transaction_total = 0, 0
        net_total = 0
        for m in cash.movements:
            if m.movement_type == MovementType.INGRESO:
                net_total += m.amount

                if m.payment_method == "EFECTIVO":
                    cash_total += m.amount
                else:
                    transaction_total += m.amount

            elif m.movement_type == MovementType.GASTO:
                net_total -= m.amount

                if m.payment_method == "EFECTIVO":
                    cash_total -= m.amount
                else:
                    transaction_total -= m.amount

        expect_balance = net_total + cash.opening_balance
        cash_total += cash.opening_balance

        return expect_balance, cash_total, transaction_total, net_total

    def _to_cash_details(self, cash: CashSession, data: tuple[int, int, int, int]) -> CashDetailPublic:
        return CashDetailPublic(
            cash_session_id=cash.cash_session_id,
            opening_balane=cash.opening_balance,
            expected_balance=data[0],
            cash_total=data[1],
            transaction_total=data[2],
            status=cash.status,
            difference=cash.difference,
            closing_balance=cash.closing_balance,
            net_total=data[3],
            opened_at=cash.opened_at,
            closed_at=cash.closed_at
        )


def get_cash_session_service(session: SessionDep) -> CashSessionService:
    return CashSessionService(session=session)


CashSessionServiceDep = Annotated[CashSessionService,
                                  Depends(get_cash_session_service)]
