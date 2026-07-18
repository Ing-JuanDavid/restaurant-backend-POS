from pydantic import BaseModel
from typing import Annotated
from fastapi import Query


class MenuItemBase(BaseModel):
    name: str
    price: Annotated[int, Query(ge=0)]
    status: bool = True
    quant: Annotated[int | None, Query(ge=0)] = None


class MenuItemCreate(MenuItemBase):
    menu_id: int


class MenuItemPublic(MenuItemBase):
    item_id: int
    menu_id: int


class MenuItemUpdate(MenuItemBase):
    menu_id: int | None = None
    name: str | None = None
    price: str | None = None
    status: bool | None = None
