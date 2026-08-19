
from sqlmodel import SQLModel, table, Field
from app.models.sales import PaymentMethod
from datetime import datetime
from enum import Enum


class ExpenseType(str, Enum):
    COMPRAS = "COMPRAS"
    GASOLINA = "GASOLINA"
    SERVICIO = "SERVICIO"
    OTRO = "OTRO"


class Expense(SQLModel, table=True):
    expense_id: int | None = Field(primary_key=True, default=None)
    amount: int = Field(gt=0)
    method: PaymentMethod = PaymentMethod.EFECTIVO
    expense_type: ExpenseType = ExpenseType.OTRO
    description: str | None = Field(max_length=200, default=None)
    movement_id: int | None = Field(
        foreign_key="cashmovement.movement_id", unique=True)
    created_at: datetime | None = None
