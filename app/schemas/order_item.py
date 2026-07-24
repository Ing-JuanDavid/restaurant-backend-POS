from sqlmodel import SQLModel, Field


class OrderItemBase(SQLModel):
    item_id: int
    quant: int = Field(gt=0)


class OrderItemPublic(OrderItemBase):
    order_item_id: int
    name: str
    unit_price: int
    total_item: int
    order_id: int


class OrderItemCreate(OrderItemBase):
    order_id: int
