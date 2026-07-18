from fastapi import APIRouter, Path, Query, status
from app.schemas.order import PublicOrder, CreateOrder, PublicOrderDetails
from app.schemas.order_item import OrderItemCreate
from app.services.order import OrderServiceDep
from typing import Annotated


router = APIRouter(prefix="/orders", tags=["order"])


@router.post("", response_model=PublicOrder, status_code=status.HTTP_201_CREATED)
async def create_order(order: CreateOrder, service: OrderServiceDep):
    return service.create_order(order=order)


@router.get("", response_model=list[PublicOrder])
async def read_orders(service: OrderServiceDep):
    return service.get_orders()


@router.get("/{document}", response_model=list[PublicOrder], status_code=200)
async def read_user_orders(document: int, service: OrderServiceDep):
    orders = service.get_orders_document(document=document)
    return orders


@router.get("/{order_id}/details")
async def read_order_items(order_id: int, service: OrderServiceDep):
    return service.get_order_details(order_id)


@router.post("/items", response_model=PublicOrderDetails)
async def add_item(item: OrderItemCreate, service: OrderServiceDep):
    db_order = service.add_item(item=item)
    return db_order


@router.patch("/items/{item_id}", response_model=PublicOrderDetails)
async def update_item(
    service: OrderServiceDep,
    item_id: int,
    new_quant: int = Query(gt=1)
):
    return service.update_item(order_item_id=item_id, new_quant=new_quant)


@router.delete("/items/{item_id}")
async def remove_item(
    service: OrderServiceDep,
    item_id: int = Path(gt=0)
):
    service.remove_item(item_id)

    return {"message": "item removed"}
