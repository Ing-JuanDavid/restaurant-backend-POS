from fastapi import APIRouter, HTTPException, status
from app.models.menu import *
from app.models.menu_item import *
from app.database import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/menu", tags=["item"])


@router.get("/all/items", response_model=list[PublicMenuItem])
async def read_all_items(session: SessionDep):
    db_items = session.exec(select(MenuItem)).all()
    return db_items


@router.get("/{menu_id}/items", response_model=list[PublicMenuItem])
async def read_menu_items(menu_id: int, session: SessionDep):

    statement = select(Menu).where(Menu.menu_id == menu_id)

    menu_db = session.exec(statement).first()

    if not menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="menu not found"
        )

    # two ways for doing a join
    # select(MenuItem).where(MenuItem.menu_id == menu_id)
    # select(MenuItem).join(Menu).where(Menu.title == menu)
    statement = select(MenuItem).where(MenuItem.menu_id == menu_db.menu_id)

    result = session.exec(statement).all()

    return result


@router.post("/items", response_model=PublicMenuItem)
async def create_menu_item(item: CreateMenuItem, session: SessionDep):
    db_menu = session.get(Menu, item.menu_id)

    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="menu not found"
        )

    db_item = MenuItem.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.put("/items/{item_id}", response_model=PublicMenuItem)
async def create_menu_item(
    item_id: int,
    item: UpdateMenuItem,
    session: SessionDep
):

    db_item = session.get(MenuItem, item_id)

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found"
        )

    item_data = item.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}")
async def create_menu_item(
    item_id: int,
    session: SessionDep
):

    db_item = session.get(MenuItem, item_id)

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found"
        )

    session.delete(db_item)
    session.commit()
    return {"messaje": "ok"}
