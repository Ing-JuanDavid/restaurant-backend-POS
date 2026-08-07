from sqlmodel import SQLModel, Field, Relationship
from app.models.customer import Customer
from datetime import datetime
from enum import Enum


class CustomerType(str, Enum):
    DEFAULT_CUSTOMER = "CONSUMIDOR FINAL"
    CUSTOMER = "CLIENTE"


class OrderStatus(str, Enum):
    PENDING = "PENDIENTE"
    READY = "LISTO"
    DELIVERED = "ENTREGADO"
    CANCELLED = "CANCELADO"


class OrderType(str, Enum):
    LOCAL = "LOCAL"
    TAKEAWAY = "PARA LLEVAR"
    DELIVERY = "DOMICILIO"


class Order(SQLModel, table=True):
    order_id: int | None = Field(primary_key=True, default=None)
    order_type: OrderType = OrderType.LOCAL
    status: OrderStatus = OrderStatus.PENDING
    total: int = Field(default=0, ge=0)
    customer_name: str | None = Field(max_length=50, default=None)
    phone: str | None = Field(max_length=20, default=None)
    delivery_address: str | None = Field(max_length=130, default=None)
    customer_id: int = Field(
        foreign_key="customer.customer_id",
        ondelete="CASCADE"
    )
    created_at: datetime | None = None

    customer: Customer | None = Relationship(back_populates="orders")

    order_details: list["OrderDetail"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }

    )
