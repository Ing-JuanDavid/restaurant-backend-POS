from sqlmodel import SQLModel, table, Field, Relationship
from datetime import datetime
from enum import Enum
from app.models.sales import PaymentMethod


class CashStatus(str, Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


class MovementType(str, Enum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"


class CashSession(SQLModel, table=True):
    cash_session_id: int | None = Field(primary_key=True, default=None)
    opening_balance: int = 0
    closing_balance: int = 0
    expec_closing_balance: int | None = 0
    difference: int | None = 0
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    status: CashStatus = CashStatus.ABIERTA

    movements: list["CashMovement"] = Relationship(back_populates="cash")


class CashMovement(SQLModel, table=True):
    movement_id: int | None = Field(primary_key=True, default=None)
    amount: int = Field(gt=0)
    payment_method: PaymentMethod
    created_at: datetime | None = None
    movement_type: MovementType | None = None
    cash_session_id: int = Field(foreign_key="cashsession.cash_session_id")
    cash: CashSession | None = Relationship(back_populates="movements")


# create expense model  *
# set the relationship between payment, expense and cashmovement
# create logic to add cash movements when a payment is created
# creteate crud for expenses
# create the same logoc to add cmovements
