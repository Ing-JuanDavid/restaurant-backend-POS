from pydantic import BaseModel
from datetime import datetime
from app.models.sales import PaymentMethod
from app.models.cash import MovementType

from app.models.cash import CashStatus


class CashBase(BaseModel):
    opening_balane: int
    status: CashStatus
    opened_at: datetime
    closed_at: datetime | None


class CashDetailPublic(CashBase):
    cash_session_id: int
    expected_balance: int
    closing_balance: int
    difference: int
    cash_total: int
    transaction_total: int
    net_total: int = 0


class CashMovementPublic(BaseModel):
    movement_id: int
    amount: int
    payment_method: PaymentMethod
    created_at: datetime
    movement_type: MovementType
