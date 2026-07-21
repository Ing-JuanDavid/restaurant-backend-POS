from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.database import Session, SessionDep
from app.services.customer import CustomerService, CustomerServiceDep

from app.schemas.order import CreateOrder, PublicOrder, PublicOrderDetails
from app.models.order import Order, CustomerType
from app.models.order_item import OrderItem
from app.schemas.customer import CustomerCreate
from datetime import date

from fastapi import Depends, HTTPException, status
from app.utils.exceptions import not_found


class OrderService:
    def __init__(self, session: Session, customer_service: CustomerService):
        self.session = session
        self.customer_service = customer_service

    def get_order(self, order_id: int) -> Order:
        db_order = self.session.get(Order, order_id)

        if not db_order:
            raise not_found("Order")

        return db_order

    def get_orders(self) -> list[PublicOrder]:
        orders = self.session.exec(select(Order).options(
            selectinload(Order.customer))).all()

        return [self.to_public_order(o) for o in orders]

    def get_orders_document(self, document: int) -> PublicOrder:
        db_customer = self.customer_service.get_customer_document(document)

        query = select(Order).where(
            Order.customer_id == db_customer.customer_id)
        orders = self.session.exec(query).all()

        return [self.to_public_order(o) for o in orders]

    def get_order_details(self, order_id: int) -> PublicOrderDetails:
        db_order = self.get_order(order_id)

        return self.to_public_order_details(db_order)

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
                CustomerCreate(
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

        return self.to_public_order(db_order)

    def to_public_order(self, o: Order) -> PublicOrder:
        return PublicOrder(
            order_id=o.order_id,
            customer_id=o.customer_id,
            total=o.total,
            date=o.date,
            order_type=o.order_type,
            status=o.status,
            document=o.customer.document if o.customer else None,
            customer_name=o.customer.name if o.customer else None,
            phone=o.customer.phone if o.customer else None
        )

    def to_public_order_details(self, o: Order) -> PublicOrderDetails:
        return PublicOrderDetails(
            order_id=o.order_id,
            customer_id=o.customer_id,
            total=o.total,
            date=o.date,
            order_type=o.order_type,
            status=o.status,
            document=o.customer.document if o.customer else None,
            customer_name=o.customer.name if o.customer else None,
            phone=o.customer.phone if o.customer else None,
            items=o.items if o.items else []
        )

    def calc_total_order(self, items: list[OrderItem]) -> int:
        total = 0
        for i in items:
            total += i.total_item
        return total


def get_order_service(
    session: SessionDep,
    customer_service: CustomerServiceDep,
):
    return OrderService(session=session, customer_service=customer_service)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
