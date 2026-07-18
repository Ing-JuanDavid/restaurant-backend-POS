from app.database import Session, SessionDep
from app.services.menu import MenuService, MenuServiceDep
from app.models.menu_item import MenuItem
from sqlmodel import select
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemPublic
from app.utils.exceptions import not_found
from fastapi import Depends
from typing import Annotated


class MenuItemService:
    def __init__(self, session: Session, menu_service: MenuService):
        self.session = session
        self.menu_service = menu_service

    def get_item(self, item_id: int) -> MenuItem:
        db_item = self.session.get(MenuItem, item_id)

        if not db_item:
            raise not_found("Item")

        return db_item

    def get_all_items(self) -> list[MenuItemPublic]:
        statement = select(MenuItem)
        items = self.session.exec(statement).all()
        return items

    def get_items_menu(self, menu_id: int) -> list[MenuItemPublic]:
        db_menu = self.menu_service.get_menu(menu_id)

        statement = select(MenuItem).where(MenuItem.menu_id == menu_id)

        items = self.session.exec(statement).all()
        return items

    def add_item(self, item: MenuItemCreate) -> MenuItemPublic:
        db_menu = self.menu_service.get_menu(item.menu_id)

        db_item = MenuItem.model_validate(item)
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def update_item(self, item_id: int, item: MenuItemUpdate) -> MenuItemPublic:
        db_item = self.get_item(item_id)

        item_data = item.model_dump(exclude_unset=True)
        db_item.sqlmodel_update(item_data)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int):
        db_item = self.get_item(item_id)
        self.session.delete(db_item)
        self.session.commit()

    def update_menu_item_quantity(self, menu_item: MenuItem, quantity_delta: int) -> None:
        if menu_item.quant is not None:
            menu_item.quant += quantity_delta
            menu_item.status = menu_item.quant > 0

        elif quantity_delta > 0 and not menu_item.status:
            menu_item.status = True


def get_menu_item_service(session: SessionDep, menu_service: MenuServiceDep):
    return MenuItemService(session=session, menu_service=menu_service)


MenuItemServiceDep = Annotated[MenuItemService, Depends(get_menu_item_service)]
