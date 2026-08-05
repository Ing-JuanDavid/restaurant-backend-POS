from enum import Enum
from sqlmodel import SQLModel, Field, table, Relationship
from datetime import datetime
from app.models.order import Order


class PaymentMethod(str, Enum):
    EFECTIVO = "EFECTIVO",
    TRANSFERENCIA = "TRANSEFERENCIA"


class Sale(SQLModel, table=True):
    sale_id: int | None = Field(primary_key=True, default=None)
    total: int | None = Field(gt=0, default=None)
    created_at: datetime | None = None
    order_id: int = Field(foreign_key="order.order_id")

    order: Order | None = Relationship()
    payments: list["Payment"] = Relationship(back_populates="sale")


class Payment(SQLModel, table=True):
    payment_id: int | None = Field(primary_key=True, default=None)
    amount: int = Field(gt=0)
    method: PaymentMethod = Field(default=PaymentMethod.EFECTIVO)
    sale_id: int = Field(foreign_key="sale.sale_id")
    sale: Sale | None = Relationship(back_populates="payments")
