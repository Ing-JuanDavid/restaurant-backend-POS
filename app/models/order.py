from sqlmodel import SQLModel, Field, Relationship
from app.models.customer import Customer
from datetime import date
from enum import Enum


class CustomerType(str, Enum):
    DEFAULT_CUSTOMER = "CONSUMIDOR FINAL"
    CUSTOMER = "CLIENTE"


class OrderStatus(str, Enum):
    PENDING = "PENDIENTE"
    READY = "LISTO"
    DELIVERED = "ENTREGADO"
    PAID = "PAGADO"
    CANCELLED = "CANCELADO"


class OrderType(str, Enum):
    LOCAL = "LOCAL"
    TAKEAWAY = "PARA_LLEVAR"
    DELIVERY = "DOMICILIO"


class Order(SQLModel, table=True):
    order_id: int | None = Field(primary_key=True, default=None)
    customer_id: int = Field(foreign_key="customer.customer_id")
    total: int = Field(default=0)
    date: date | None = Field(default=None)

    order_type: OrderType = Field(default=OrderType.LOCAL)
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    customer: Customer | None = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")
