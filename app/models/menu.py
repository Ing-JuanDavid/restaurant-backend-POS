# menu models

from sqlmodel import SQLModel, Field


class BaseMenu(SQLModel):
    title: str = Field(max_length=20)


class Menu(BaseMenu, table=True):
    menu_id: int | None = Field(primary_key=True, default=None)


class PublicMenu(BaseMenu):
    menu_id: int
