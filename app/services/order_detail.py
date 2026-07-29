from app.database import Session, SessionDep
from app.services.order import OrderService, OrderServiceDep
from app.services.menu_item import MenuItemService, MenuItemServiceDep
from typing import Annotated
from fastapi import Depends
from app.utils.exceptions import not_found, not_available, invalid
from app.models.order_detail import OrderDetail
from app.schemas.order_detail import OrderDetailCreate, OrderDetailPublic
from app.schemas.order import OrderDetailsPublic


class OrderItemService:

    def __init__(self, session: Session, order_service: OrderService, menu_item_service: MenuItemService):
        self.session = session
        self.order_service = order_service
        self.menu_item_service = menu_item_service

    def get_item(self, order_item_id: int) -> OrderDetail:
        db_order_item = self.session.get(OrderDetail, order_item_id)

        if not db_order_item:
            raise not_found("Item")
        return db_order_item

    def add_item(self, item: OrderDetailCreate) -> OrderDetailsPublic:
        db_order = self.order_service.get_order(item.order_id)
        db_menu_item = self.menu_item_service.get_item(item.item_id)

        db_order_item = OrderDetail.model_validate(item)

        # validation status
        if not db_menu_item.status:
            raise not_available(db_menu_item.name)

        if db_menu_item.quant is not None:
            if item.quantity > db_menu_item.quant:
                raise invalid("quant")

            self.menu_item_service.update_item_quantity(
                db_menu_item,
                -item.quantity
            )

        db_order_item.unit_price = db_menu_item.price
        db_order_item.subtotal = db_menu_item.price * item.quantity
        db_order.order_details.append(db_order_item)
        db_order.total = self.order_service.calc_total_order(
            db_order.order_details)
        self.session.commit()
        self.session.refresh(db_order)
        return self.order_service.to_public_order_details(db_order)

    # make update item order function

    def update_item(self, order_item_id: int, new_quant: int) -> OrderDetailsPublic:
        db_order_item = self.get_item(order_item_id)
        db_menu_item = db_order_item.menu_item
        db_order = db_order_item.order
        old_quant = db_order_item.quantity
        difference = new_quant - old_quant

        # Validar aumento
        if difference > 0:
            if db_menu_item.quant is not None and difference > db_menu_item.quant:
                raise invalid("quant")

        # Actualizar inventario

        self.menu_item_service.update_item_quantity(
            db_menu_item, -difference)

        # Actualizar item
        db_order_item.quantity = new_quant
        db_order_item.subtotal = new_quant * db_menu_item.price

        # Recalcular total
        db_order.total = self.order_service.calc_total_order(
            db_order.order_details)

        self.session.commit()
        self.session.refresh(db_order)

        return self.order_service.to_public_order_details(db_order)

    def remove_item(self, order_item_id):
        db_order_item = self.get_item(order_item_id)
        db_menu_item = db_order_item.menu_item
        db_order = db_order_item.order

        if not db_menu_item or not db_order:
            raise not_found("Order or menu item")

        self.menu_item_service.update_item_quantity(
            db_menu_item,
            db_order_item.quantity
        )

        db_order.order_details.remove(db_order_item)
        db_order.total = self.order_service.calc_total_order(
            db_order.order_details)
        self.session.commit()


def get_order_item_service(
    session: SessionDep,
    order_service: OrderServiceDep,
    menu_item_service: MenuItemServiceDep
) -> OrderItemService:
    return OrderItemService(session=session, order_service=order_service, menu_item_service=menu_item_service)


OrderItemServiceDep = Annotated[OrderItemService,
                                Depends(get_order_item_service)]
