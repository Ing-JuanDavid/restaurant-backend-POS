from enum import Enum
from sqlmodel import SQLModel, Field, table, Relationship
from datetime import datetime


class PaymentMethod(str, Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"


class SaleStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIALMENTE_PAGADA"
    PAGADA = "PAGADA"


class Sale(SQLModel, table=True):
    sale_id: int | None = Field(primary_key=True, default=None)
    total: int | None = Field(gt=0, default=None)
    status: SaleStatus = SaleStatus.PENDIENTE
    created_at: datetime | None = None
    order_id: int = Field(foreign_key="order.order_id")
    order: "Order" = Relationship(back_populates="sale")
    payments: list["Payment"] = Relationship(back_populates="sale")


class Payment(SQLModel, table=True):
    payment_id: int | None = Field(primary_key=True, default=None)
    amount: int = Field(gt=0)
    method: PaymentMethod = PaymentMethod.EFECTIVO
    created_at: datetime | None = None
    sale_id: int = Field(foreign_key="sale.sale_id")
    sale: Sale | None = Relationship(back_populates="payments")
