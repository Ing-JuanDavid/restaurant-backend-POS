from app.models.order import OrderType, OrderStatus, CustomerType
from pydantic import BaseModel, Field
from app.schemas.order_item import OrderItemPublic
from datetime import datetime


class OrderBase(BaseModel):
    status: OrderStatus = OrderStatus.PENDING
    order_type: OrderType = OrderType.LOCAL
    document: int | None = None
    customer_name: str | None = Field(max_length=20, default=None)
    cellphone: str | None = Field(max_length=12, default=None)
    address: None | str = Field(max_length=50, default=None)


class OrderCreate(OrderBase):
    customer_type: CustomerType = CustomerType.DEFAULT_CUSTOMER


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    order_type: OrderType | None = None
    document: int | None = None
    customer_name: str | None = None
    cellphone: str | None = None
    address: str | None = None


class OrderPublic(OrderBase):
    order_id: int
    customer_name: str | None
    cellphone: str | None
    total: int
    created_at: datetime


class OrderDetailsPublic(OrderPublic):
    items: list[OrderItemPublic]
