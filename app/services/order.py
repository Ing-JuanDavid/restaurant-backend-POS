from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.database import SessionDep
from typing import Annotated
from app.services.customer import CustomerServiceDep

from app.schemas.order import *
from app.schemas.order_item import OrderItemCreate
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.customer import BaseCustomer
from datetime import date

from fastapi import Depends, HTTPException, status
from app.utils.exceptions import not_found, invalid


class OrderService:
    def __init__(self, session: SessionDep, customer_service: CustomerServiceDep):
        self.session = session
        self.customer_service = customer_service

    def get_orders(self) -> list[PublicOrder]:
        orders = self.session.exec(select(Order).options(
            selectinload(Order.customer))).all()

        return [to_public_order(o) for o in orders]

    def create_order(self, order: CreateOrder) -> PublicOrder:
        db_customer = None

        if (order.customer_type == CustomerType.CUSTOMER and not order.document):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="debe ingresar el documento"
            )

        if (order.customer_type == CustomerType.DEFAULT_CUSTOMER):
            db_customer = self.customer_service.get_customer(0)
        else:
            db_customer = self.customer_service.get_customer(order.document)

        if not db_customer:
            db_customer = self.customer_service.create_customer(
                BaseCustomer(
                    document=order.document,
                    name=f"customer-{order.document}"
                )
            )

        db_order = Order(
            customer_id=db_customer.customer_id,
            order_type=order.order_type,
            status=order.status,
            date=date.today(),
        )

        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order, attribute_names=["customer"])

        return to_public_order(db_order)

    def add_item(self, item: OrderItemCreate) -> PublicOrder:

        db_order_item = OrderItem.model_validate(item)

        db_order = self.session.get(Order, item.order_id)
        db_menu_item = self.session.get(MenuItem, item.item_id)

        if not db_order:
            raise not_found("order")

        if not db_menu_item:
            raise not_found("item")

        if db_menu_item.quant:

            if item.quant > db_menu_item.quant:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="invalid quant"
                )
        else:
            if db_menu_item.quant == 0 and db_menu_item.status:
                db_menu_item.status = False
                self.session.commit()

        if (db_menu_item.status == False):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="item not available"
            )

        total_item = item.quant * db_menu_item.price

        db_order_item.total_item = total_item
        db_order.items.append(db_order_item)
        db_order.total = calc_total_order(db_order.items)

        if (db_menu_item.quant):
            db_menu_item.quant -= item.quant

        self.session.commit()
        self.session.refresh(db_order)

        return to_public_order(db_order)


# make update item order function

    def update_item(self, order_item_id: int, new_quat: int) -> PublicOrder:
        db_order_item = self.session.get(OrderItem, order_item_id)

        if not db_order_item:
            raise not_found("order item")

        db_menu_item = self.session.get(MenuItem, db_order_item.item_id)

        if (new_quat < db_order_item.quant):
            quant_diference = db_order_item.quant - new_quat
            db_menu_item.quant += quant_diference

            if (db_menu_item.status == False):
                db_menu_item.status = True

        if (new_quat > db_order_item.quant):
            if new_quat > db_menu_item.quant:
                raise invalid("quant")

            quant_diference = new_quat - db_order_item.quant

            db_menu_item.quant -= quant_diference

        data_quant = {
            "quant": new_quat,
            "total_item": db_menu_item.price*new_quat
        }

        db_order_item.sqlmodel_update(data_quant)
        self.session.commit()

        db_order = self.session.get(Order, db_order_item.order_id)

        db_order.total = calc_total_order(db_order.items)
        self.session.commit()
        self.session.refresh(db_order)
        return to_public_order(db_order)


def to_public_order(o: Order) -> PublicOrder:
    return PublicOrder(
        order_id=o.order_id,
        customer_id=o.customer_id,
        total=o.total,
        date=o.date,
        order_type=o.order_type,
        status=o.status,
        document=o.customer.document if o.customer else None,
        items=o.items if o.items else []
    )


def calc_total_order(items: list[OrderItem]) -> int:
    total = 0
    for i in items:
        total += i.total_item
    return total


def get_order_service(
    session: SessionDep,
    customer_service: CustomerServiceDep
):
    return OrderService(session=session, customer_service=customer_service)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
