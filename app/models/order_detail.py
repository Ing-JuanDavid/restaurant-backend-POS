from sqlmodel import SQLModel, table, Field, Relationship
from app.models.menu_item import MenuItem
from app.models.order import Order


class OrderDetail(SQLModel, table=True):
    detail_id: int | None = Field(default=None, primary_key=True)
    quantity: int = Field(ge=0)
    unit_price: int | None = None
    subtotal: int | None = None
    item_id: int = Field(foreign_key="menuitem.item_id")
    order_id: int = Field(foreign_key="order.order_id")

    order: Order | None = Relationship(back_populates="order_details")
    menu_item: MenuItem | None = Relationship(back_populates="order_details")
