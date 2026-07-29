from sqlmodel import SQLModel, Field


class OrderDetailBase(SQLModel):
    item_id: int
    quantity: int = Field(gt=0)


class OrderDetailCreate(OrderDetailBase):
    order_id: int


class OrderDetailPublic(OrderDetailBase):
    detail_id: int
    unit_price: int
    subtotal: int
    order_id: int
