from app.database import Session, SessionDep
from app.models.menu import Menu
from sqlmodel import select
from app.schemas.menu import MenuBase, MenuUpdate, MenuPublic
from app.utils.exceptions import not_found
from fastapi import Depends
from typing import Annotated


class MenuService:
    def __init__(self, session: Session):
        self.session = session

    def get_menues(self, offset: int, limit: int) -> list[MenuPublic]:
        statement = select(Menu).offset(offset).limit(limit)
        menues = self.session.exec(statement).all()
        return menues

    def create_menu(self, menu: MenuBase) -> MenuPublic:
        db_menu = Menu.model_validate(menu)
        self.session.add(db_menu)
        self.session.commit()
        self.session.refresh(db_menu)
        return db_menu

    def get_menu(self, menu_id: int) -> Menu:
        db_menu = self.session.get(Menu, menu_id)

        if not db_menu:
            raise not_found("Menu")

        return db_menu

    def update_menu(self, menu_id: int, upd_menu: MenuUpdate) -> MenuPublic:

        menu_db = self.get_menu(menu_id)

        menu_data = upd_menu.model_dump(exclude_unset=True)
        menu_db.sqlmodel_update(menu_data)
        self.session.commit()
        self.session.refresh(menu_db)
        return menu_db

    def delete_menu(self, menu_id: int):
        menu_db = self.get_menu(menu_id)
        self.session.delete(menu_db)
        self.session.commit()


def get_menu_service(session: SessionDep):
    return MenuService(session=session)


MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
