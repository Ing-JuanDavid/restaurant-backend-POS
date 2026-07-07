from sqlmodel import SQLModel, Field


class OrderItemBase(SQLModel):
    item_id: int
    quant: int = Field(gt=0)


class OrderItemPublic(OrderItemBase):
    id: int
    order_id: int
    total_item: int


class OrderItemCreate(OrderItemBase):
    order_id: int
