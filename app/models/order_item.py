from sqlmodel import SQLModel, table, Field, Relationship
from app.models.menu_item import MenuItem
from app.models.order import Order


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="menuitem.item_id")
    name: str | None = Field(default=None)
    order_id: int = Field(foreign_key="order.order_id")
    quant: int
    unit_price: int | None = None
    total_item: int | None = None
    order: Order | None = Relationship(back_populates="items")
    menu_item: MenuItem | None = Relationship(back_populates="order_items")
