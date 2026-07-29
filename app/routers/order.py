from fastapi import APIRouter, Path, Query, status
from typing import Annotated
from app.models.order import OrderStatus, CustomerType
from app.schemas.order import OrderCreate, OrderUpdate, OrderPublic, OrderDetailsPublic
from app.schemas.order_detail import OrderDetailCreate
from app.services.order import OrderServiceDep
from app.services.order_detail import OrderItemServiceDep


router = APIRouter(prefix="/orders", tags=["order"])


@router.post("", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, service: OrderServiceDep):
    return service.create_order(order=order)


@router.get("", response_model=list[OrderPublic])
async def read_orders(
    service: OrderServiceDep,
    status: Annotated[OrderStatus | None, Query(
        description="Filter by order status")] = None,
    customer_type: Annotated[CustomerType | None, Query()] = None
):
    return service.get_orders(status, customer_type)


@router.get("/{document}", response_model=list[OrderPublic], status_code=200)
async def read_user_orders(document: int, service: OrderServiceDep):
    orders = service.get_orders_document(document=document)
    return orders


@router.get("/{order_id}/details")
async def read_order_items(order_id: int, service: OrderServiceDep):
    return service.get_order_details(order_id)


@router.patch("/{order_id}", response_model=OrderPublic)
async def update_order(
    order: OrderUpdate,
    service: OrderServiceDep,
    order_id: int = Path(gt=0)
):
    return service.update_order(order_id, order)


@router.post("/details", response_model=OrderDetailsPublic)
async def add_detail(order_detail: OrderDetailCreate, service: OrderItemServiceDep):
    db_order = service.add_order_detail(order_detail=order_detail)
    return db_order


@router.patch("/details/{detail_id}", response_model=OrderDetailsPublic)
async def update_detail(
    service: OrderItemServiceDep,
    detail_id: int,
    new_quant: int = Query(gt=0)
):
    return service.update_order_detail(order_detail_id=detail_id, new_quant=new_quant)


@router.delete("/details/{detail_id}")
async def remove_detail(
    service: OrderItemServiceDep,
    detail_id: int = Path(gt=0)
):
    service.remove_order_detail(detail_id)

    return {"message": "detail removed"}
