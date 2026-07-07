from fastapi import APIRouter, Query
from app.database import SessionDep
from app.schemas.order import PublicOrder, CreateOrder
from app.schemas.order_item import OrderItemCreate
from app.services.order import OrderServiceDep
from app.models.order import Order
from typing import Annotated


router = APIRouter(prefix="/orders", tags=["order"])


@router.post("", response_model=PublicOrder)
async def create_order(order: CreateOrder, service: OrderServiceDep):
    return service.create_order(order=order)


@router.get("", response_model=list[PublicOrder])
async def get_orders(service: OrderServiceDep):
    return service.get_orders()


@router.post("/items", response_model=PublicOrder)
async def add_item(item: OrderItemCreate, service: OrderServiceDep):
    db_order = service.add_item(item=item)
    return db_order


@router.post("/items/{item_id}", response_model=PublicOrder)
async def update_item(item_id: int, new_quant: Annotated[int, Query(ge=1)], service: OrderServiceDep):
    db_order = service.update_item(order_item_id=item_id, new_quat=new_quant)
    return db_order
