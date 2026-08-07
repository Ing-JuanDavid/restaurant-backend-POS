from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.database import Session, SessionDep
from app.services.customer import CustomerService, CustomerServiceDep
from app.services.sales import SalesService, SalesServiceDep

from app.schemas.order import OrderCreate, OrderUpdate, OrderPublic, OrderDetailsPublic
from app.models.order import Order, CustomerType, OrderStatus
from app.models.order_detail import OrderDetail
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate
from datetime import datetime

from fastapi import Depends, HTTPException, status
from app.utils.exceptions import not_found


class OrderService:
    def __init__(self, session: Session, customer_service: CustomerService, sales_service: SalesService):
        self.session = session
        self.customer_service = customer_service
        self.sales_service = sales_service

    def get_order(self, order_id: int) -> Order:
        db_order = self.session.get(Order, order_id)

        if not db_order:
            raise not_found("Order")

        return db_order

    def get_orders(self, status: OrderStatus | None, customer_type: CustomerType | None) -> list[OrderPublic]:

        query = (select(Order).options(selectinload(
            Order.customer)).order_by(Order.created_at))

        if status is not None:
            query = query.where(Order.status == status)

        if customer_type is not None:
            query = query.join(Order.customer)
            if customer_type == CustomerType.DEFAULT_CUSTOMER:
                query = query.where(Customer.document == 0)
            else:
                query = query.where(Customer.document != 0)

        orders = self.session.exec(query).all()

        return [self.to_public_order(o) for o in orders]

    def get_orders_document(self, document: int) -> OrderPublic:
        db_customer = self.customer_service.get_customer_document(document)

        query = select(Order).where(
            Order.customer_id == db_customer.customer_id)
        orders = self.session.exec(query).all()

        return [self.to_public_order(o) for o in orders]

    def get_order_details(self, order_id: int) -> OrderDetailsPublic:
        db_order = self.get_order(order_id)

        return self.to_public_order_details(db_order)

    def create_order(self, order: OrderCreate) -> OrderPublic:
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
            created_at=datetime.now(),
            customer_name=order.customer_name if order.customer_name else db_customer.name,
            phone=order.phone if order.phone else db_customer.cellphone,
            delivery_address=order.delivery_address if order.delivery_address else db_customer.address
        )

        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order, attribute_names=["customer"])

        self.sales_service.create_sale(db_order)

        return self.to_public_order(db_order)

    def update_order(self, order_id: int, upd_order: OrderUpdate) -> OrderPublic:
        db_order = self.get_order(order_id)

        order_data = upd_order.model_dump(exclude_unset=True)

        db_order.sqlmodel_update(order_data)
        self.session.commit()
        self.session.refresh(db_order)
        return self.to_public_order(db_order)

    def to_public_order(self, o: Order) -> OrderPublic:
        return OrderPublic(
            order_id=o.order_id,
            customer_id=o.customer_id,
            total=o.total,
            created_at=o.created_at,
            order_type=o.order_type,
            status=o.status,
            document=o.customer.document if o.customer else None,
            customer_name=o.customer_name,
            phone=o.phone,
            delivery_address=o.delivery_address
        )

    def to_public_order_details(self, o: Order) -> OrderDetailsPublic:
        return OrderDetailsPublic(
            order_id=o.order_id,
            customer_id=o.customer_id,
            total=o.total,
            created_at=o.created_at,
            order_type=o.order_type,
            status=o.status,
            document=o.customer.document if o.customer else None,
            customer_name=o.customer_name,
            phone=o.phone,
            delivery_address=o.delivery_address,
            items=o.order_details if o.order_details else []
        )

    def calc_total_order(self, items: list[OrderDetail]) -> int:
        total = 0
        for i in items:
            total += i.subtotal
        return total


def get_order_service(
    session: SessionDep,
    customer_service: CustomerServiceDep,
    sales_service: SalesServiceDep
):
    return OrderService(session=session, customer_service=customer_service, sales_service=sales_service)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
