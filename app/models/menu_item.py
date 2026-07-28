from sqlmodel import SQLModel, Field, Relationship


class MenuItem(SQLModel, table=True):
    item_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    price: int = Field(ge=0)
    status: bool = True
    quant: int | None = Field(ge=0)
    menu_id: int = Field(foreign_key="menu.menu_id")
    order_details: list["OrderDetail"] = Relationship(
        back_populates="menu_item")
