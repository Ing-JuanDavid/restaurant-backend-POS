from fastapi import APIRouter, Query, status
from app.schemas.menu import MenuBase, MenuUpdate, MenuPublic
from typing import Annotated
from app.services.menu import MenuServiceDep

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=list[MenuPublic])
async def read_menues(
    service: MenuServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return service.get_menues(offset, limit)


@router.post("", response_model=MenuPublic, status_code=status.HTTP_201_CREATED)
async def create_menu(menu: MenuBase, service: MenuServiceDep):
    db_menu = service.create_menu(menu)
    return db_menu


@router.get("/{menu_id}", response_model=MenuPublic)
async def find_menu(menu_id: int, service: MenuServiceDep):
    return service.get_menu(menu_id)


@router.patch("/{menu_id}", response_model=MenuPublic)
async def update_menu(
        menu_id: int,
        upd_menu: MenuUpdate,
        service: MenuServiceDep):

    return service.update_menu(menu_id, upd_menu)


@router.delete("/{menu_id}")
async def delete_menu(menu_id: int, service: MenuServiceDep):
    service.delete_menu(menu_id)
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
