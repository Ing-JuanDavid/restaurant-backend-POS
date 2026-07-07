
from sqlmodel import SQLModel, Field

# menu_items


class BaseMenuItem(SQLModel):
    name: str
    price: int
    status: bool = Field(default=True)
    quant: int | None = Field(default=None)


class MenuItem(BaseMenuItem, table=True):
    item_id: int | None = Field(default=None, primary_key=True)
    menu_id: int = Field(foreign_key="menu.menu_id")
    # category_id: int = Field(foreign_key="category.category_id")


class CreateMenuItem(BaseMenuItem):
    menu_id: int
    # category_id: int


class PublicMenuItem(BaseMenuItem):
    item_id: int
    menu_id: int
    # category_id: int


class UpdateMenuItem(BaseMenuItem):
    menu_id: int | None = None
    name: str | None = None
    price: str | None = None
    status: bool | None = None
