from sqlmodel import SQLModel, table, Field, Relationship
from app.models.menu_item import MenuItem
from app.models.order import Order


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    quant: int = Field(ge=0)
    unit_price: int | None = None
    total_item: int | None = None

    item_id: int = Field(foreign_key="menuitem.item_id")
    order_id: int = Field(foreign_key="order.order_id")
    order: Order | None = Relationship(back_populates="items")
    menu_item: MenuItem | None = Relationship(back_populates="order_items")
