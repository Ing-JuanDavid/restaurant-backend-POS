from fastapi import APIRouter, status
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemPublic
from app.services.menu_item import MenuItemServiceDep

router = APIRouter(prefix="/menu", tags=["item"])


@router.get("/all/items", response_model=list[MenuItemPublic])
async def read_all_items(service: MenuItemServiceDep):
    return service.get_all_items()


@router.get("/{menu_id}/items", response_model=list[MenuItemPublic])
async def read_menu_items(menu_id: int, service: MenuItemServiceDep):
    return service.get_items_menu(menu_id)


@router.post("/items", response_model=MenuItemPublic, status_code=status.HTTP_201_CREATED)
async def create_menu_item(item: MenuItemCreate, service: MenuItemServiceDep):
    return service.add_item(item)


@router.patch("/items/{item_id}", response_model=MenuItemPublic)
async def update_menu_item(
    item_id: int,
    upd_item: MenuItemUpdate,
    service: MenuItemServiceDep
):
    return service.update_item(item_id, upd_item)


@router.delete("/items/{item_id}")
async def create_menu_item(
    item_id: int,
    service: MenuItemServiceDep
):

    service.delete_item(item_id)
    return {"messaje": "ok"}
