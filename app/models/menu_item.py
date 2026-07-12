from sqlmodel import SQLModel, Field, Relationship


class MenuItem(SQLModel, table=True):
    item_id: int | None = Field(default=None, primary_key=True)
    name: str
    price: int
    status: bool = Field(default=True)
    quant: int | None = Field(default=None)
    menu_id: int = Field(foreign_key="menu.menu_id")
    order_items: list["OrderItem"] = Relationship(back_populates="menu_item")
