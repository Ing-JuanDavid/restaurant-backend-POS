from pydantic import BaseModel
from datetime import datetime

from app.models.cash import CashStatus


class CashBase(BaseModel):
    opening_balane: int
    status: CashStatus
    opened_at: datetime
    closed_at: datetime


class CashDetailPublic(CashBase):
    cash_session_id: int
    expected_balance: int
