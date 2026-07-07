from fastapi import APIRouter, Query, HTTPException, status
from app.database import SessionDep
from sqlmodel import select
from app.models.menu import *
from typing import Annotated

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=list[PublicMenu])
async def read_menues(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    menues = session.exec(select(Menu).offset(offset).limit(limit)).all()
    return menues


@router.post("", response_model=PublicMenu)
async def create_menu(menu: BaseMenu, session: SessionDep):
    db_menu = Menu.model_validate(menu)
    session.add(db_menu)
    session.commit()
    session.refresh(db_menu)
    return db_menu


@router.get("/{menu_id}", response_model=PublicMenu)
async def find_menu(menu_id: int, session: SessionDep):
    db_menu = session.get(Menu, menu_id)

    if not db_menu:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="menu not found"
        )

    return db_menu


@router.put("/{menu_id}", response_model=PublicMenu)
async def update_menu(
        menu_id: int,
        menu: BaseMenu,
        session: SessionDep):

    menu_db = session.get(Menu, menu_id)

    if not menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="menu not found"
        )

    menu_data = menu.model_dump(exclude_unset=True)
    menu_db.sqlmodel_update(menu_data)
    session.add(menu_db)
    session.commit()
    session.refresh(menu_db)
    return menu_db


@router.delete("/{menu_id}")
async def delete_menu(menu_id: int, session: SessionDep):

    menu_db = session.get(Menu, menu_id)

    if not menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="menu not found"
        )

    session.delete(menu_db)
    session.commit()

    return {"message": "ok"}


# @router.get("/{menu}/items", response_model=list[PublicMenuItem])
# async def read_menu_itemns(menu: str, session: SessionDep):

#     statement = select(Menu).where(Menu.title == menu)

#     db_menu = session.exec(statement).first()

#     if not db_menu:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="category not found"
#         )

#     # two ways for doing a join
#     # select(MenuItem).where(MenuItem.menu_id == menu_id)
#     # select(MenuItem).join(Menu).where(Menu.title == menu)
#     statement = select(MenuItem).where(
#         MenuItem.menu_id == db_menu.menu_id)

#     result = session.exec(statement).all()

#     return result
