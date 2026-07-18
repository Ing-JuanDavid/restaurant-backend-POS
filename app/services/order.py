from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.database import Session, SessionDep
from app.services.customer import CustomerService, CustomerServiceDep
from app.services.menu_item import MenuItemService, MenuItemServiceDep

from app.schemas.order import CreateOrder, PublicOrder, PublicOrderDetails
from app.schemas.order_item import OrderItemCreate
from app.models.order import Order, CustomerType
from app.models.order_item import OrderItem
from app.schemas.customer import CustomerCreate
from datetime import date

from fastapi import Depends, HTTPException, status
from app.utils.exceptions import not_found, invalid, not_available


class OrderService:
    def __init__(self, session: Session, customer_service: CustomerService, menu_item_service: MenuItemService):
        self.session = session
        self.customer_service = customer_service
        self.menu_item_service = menu_item_service

    def get_order(self, order_id: int) -> Order:
        db_order = self.session.get(Order, order_id)

        if not db_order:
            raise not_found("Order")

        return db_order

    def get_orders(self) -> list[PublicOrder]:
        orders = self.session.exec(select(Order).options(
            selectinload(Order.customer))).all()

        return [to_public_order(o) for o in orders]

    def get_orders_document(self, document: int) -> PublicOrder:
        db_customer = self.customer_service.get_customer_document(document)

        query = select(Order).where(
            Order.customer_id == db_customer.customer_id)
        orders = self.session.exec(query).all()

        return [to_public_order(o) for o in orders]

    def get_order_details(self, order_id: int) -> PublicOrderDetails:
        db_order = self.get_order(order_id)

        return to_public_order_details(db_order)

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

        return to_public_order(db_order)

    def get_item(self, order_item_id: int) -> OrderItem:
        db_order_item = self.session.get(OrderItem, order_item_id)

        if not db_order_item:
            raise not_found("Item")
        return db_order_item

    def add_item(self, item: OrderItemCreate) -> PublicOrderDetails:
        db_order = self.get_order(item.order_id)
        db_menu_item = self.menu_item_service.get_item(item.item_id)

        db_order_item = OrderItem.model_validate(item)
        db_order_item.name = db_menu_item.name

        # validation status
        if not db_menu_item.status:
            raise not_available(db_menu_item.name)

        if db_menu_item.quant is not None:
            if item.quant > db_menu_item.quant:
                raise invalid("quant")

            self.menu_item_service.update_menu_item_quantity(
                db_menu_item,
                -item.quant
            )

        db_order_item.unit_price = db_menu_item.price
        db_order_item.total_item = db_menu_item.price * item.quant
        db_order.items.append(db_order_item)
        db_order.total = calc_total_order(db_order.items)
        self.session.commit()
        self.session.refresh(db_order)
        return to_public_order_details(db_order)

    # make update item order function

    def update_item(self, order_item_id, new_quant: int) -> PublicOrderDetails:
        db_order_item = self.get_item(order_item_id)
        db_menu_item = db_order_item.menu_item
        db_order = db_order_item.order
        old_quant = db_order_item.quant
        difference = new_quant - old_quant

        # Validar aumento
        if difference > 0:
            if db_menu_item.quant is not None and difference > db_menu_item.quant:
                raise invalid("quant")

        # Actualizar inventario

        self.menu_item_service.update_menu_item_quantity(
            db_menu_item, -difference)

        # Actualizar item
        db_order_item.quant = new_quant
        db_order_item.total_item = new_quant * db_menu_item.price

        # Recalcular total
        db_order.total = calc_total_order(db_order.items)

        self.session.commit()
        self.session.refresh(db_order)

        return to_public_order_details(db_order)

    def remove_item(self, order_item_id):
        db_order_item = self.get_item(order_item_id)
        db_menu_item = db_order_item.menu_item
        db_order = db_order_item.order

        if not db_menu_item or not db_order:
            raise not_found("Order or menu item")

        self.menu_item_service.update_menu_item_quantity(
            db_menu_item,
            db_order_item.quant
        )

        db_order.items.remove(db_order_item)
        db_order.total = calc_total_order(db_order.items)
        self.session.commit()


def to_public_order(o: Order) -> PublicOrder:
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


def to_public_order_details(o: Order) -> PublicOrderDetails:
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


def calc_total_order(items: list[OrderItem]) -> int:
    total = 0
    for i in items:
        total += i.total_item
    return total


def get_order_service(
    session: SessionDep,
    customer_service: CustomerServiceDep,
    menu_item_service: MenuItemServiceDep
):
    return OrderService(session=session, customer_service=customer_service, menu_item_service=menu_item_service)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
