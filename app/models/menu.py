# menu models

from sqlmodel import SQLModel, Field


class Menu(SQLModel, table=True):
    menu_id: int | None = Field(primary_key=True, default=None)
    title: str = Field(max_length=20)
    description: str | None = Field(default=None, max_length=150)

    # add a raleationship to item_menu
