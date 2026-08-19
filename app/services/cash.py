from app.database import Session, SessionDep
from app.models.cash import CashSession, CashStatus
from typing import Annotated
from fastapi import Depends
from app.models.cash import MovementType
from app.schemas.cash import CashDetailPublic
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
        expected_balance = self._get_expected_closing_balcance(db_cash)
        return self._to_cash_details(db_cash, expected_balance)

    def get_opened_cash(self) -> CashSession | None:
        statement = select(CashSession).where(
            CashSession.status == CashStatus.ABIERTA)
        return self.session.exec(statement).first()

    def open_cash(self, opening_balance: int | None) -> CashSession:

        is_opened_cash = self.get_opened_cash()

        if is_opened_cash:
            raise opened_cash(is_opened_cash.cash_session_id)

        db_cash = CashSession()
        db_cash.opening_balance = opening_balance if opening_balance is not None else 0
        db_cash.status = CashStatus.ABIERTA
        db_cash.opened_at = datetime.now()
        self.session.add(db_cash)
        self.save_cash(db_cash)
        return db_cash

    def close_cash(self, cash_id: int, closing_balance: int) -> CashSession:
        db_cash = self.get_cash(cash_id)

        if db_cash.status == CashStatus.CERRADA:
            raise invalid_action("close cash")

        expect_balance = self._get_expected_closing_balcance(db_cash)

        db_cash.closing_balance = closing_balance
        db_cash.expec_closing_balance = expect_balance
        db_cash.difference = closing_balance - expect_balance
        db_cash.status = CashStatus.CERRADA
        db_cash.closed_at = datetime.now()

        self.save_cash(db_cash)
        return db_cash

    def save_cash(self, cash: CashSession):
        self.session.commit()
        self.session.refresh(cash)

    def _get_expected_closing_balcance(self, cash: CashSession) -> int:
        expect_balance = 0
        for m in cash.movememts:
            if m.movement_type == MovementType.INGRESO:
                expect_balance += m.amount
            elif m.movement_type == MovementType.GASTO:
                expect_balance -= m.amount

        expect_balance += cash.opening_balance
        return expect_balance

    def _to_cash_details(self, cash: CashSession, expect_balance: int):
        cash_detail = CashDetailPublic.model_validate(cash)
        cash_detail.expected_balance = expect_balance
        return cash_detail


def get_cash_session_service(session: SessionDep) -> CashSessionService:
    return CashSessionService(session=session)


CashSessionDep = Annotated[CashSessionService,
                           Depends(get_cash_session_service)]
