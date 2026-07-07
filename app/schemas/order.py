from app.models.order import OrderType, OrderStatus, CustomerType
from sqlmodel import SQLModel
from app.schemas.order_item import OrderItemPublic


class BaseOrder(SQLModel):
    status: OrderStatus = OrderStatus.PENDING
    order_type: OrderType = OrderType.LOCAL


class CreateOrder(BaseOrder):
    document: int | None
    customer_type: CustomerType = CustomerType.DEFAULT_CUSTOMER


class UpdateOrder(SQLModel):
    status: OrderStatus | None = None
    order_type: OrderType | None = None
    document: int | None = None


class PublicOrder(BaseOrder):
    order_id: int
    document: int
    total: int
    items: list[OrderItemPublic]
