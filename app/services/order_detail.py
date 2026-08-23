from app.database import Session, SessionDep
from app.services.order import OrderService, OrderServiceDep
from app.services.menu_item import MenuItemService, MenuItemServiceDep
from typing import Annotated
from fastapi import Depends
from app.utils.exceptions import not_found, not_available, invalid, invalid_action
from app.models.order import OrderStatus
from app.models.sales import SaleStatus
from app.models.order_detail import OrderDetail
from app.schemas.order_detail import OrderDetailCreate, OrderDetailPublic
from app.schemas.order import OrderDetailsPublic


class OrderDetailService:

    def __init__(self, session: Session, order_service: OrderService, menu_item_service: MenuItemService):
        self.session = session
        self.order_service = order_service
        self.menu_item_service = menu_item_service

    def get_order_detail(self, detail_id: int) -> OrderDetail:
        db_order_detail = self.session.get(OrderDetail, detail_id)

        if not db_order_detail:
            raise not_found("detail")
        return db_order_detail

    def add_order_detail(self, order_detail: OrderDetailCreate) -> OrderDetailsPublic:
        db_order = self.order_service.get_order(order_detail.order_id)
        db_sale = db_order.sale
        db_menu_item = self.menu_item_service.get_item(order_detail.item_id)

        db_order_detail = OrderDetail.model_validate(order_detail)

        if not db_order.status == OrderStatus.PENDING or db_sale.status == SaleStatus.PAGADA:
            raise invalid_action("add detail")

        # validation status
        if not db_menu_item.status:
            raise not_available(f"item {order_detail.item_id}")

        if db_menu_item.quant is not None:
            if order_detail.quantity > db_menu_item.quant:
                raise invalid("quantity")

            self.menu_item_service.update_item_quantity(
                db_menu_item,
                -order_detail.quantity
            )

        db_order_detail.product_name = db_menu_item.name
        db_order_detail.unit_price = db_menu_item.price
        db_order_detail.subtotal = db_order_detail.unit_price * order_detail.quantity
        db_order.order_details.append(db_order_detail)
        self.order_service.update_order_totals(db_order)
        return self.order_service.to_public_order_details(self.order_service.save_order(db_order))

    # make update item order function

    def update_order_detail(self, order_detail_id: int, new_quant: int) -> OrderDetailsPublic:
        db_order_detail = self.get_order_detail(order_detail_id)
        db_menu_item = db_order_detail.menu_item
        db_order = db_order_detail.order
        db_sale = db_order.sale
        old_quant = db_order_detail.quantity
        difference = new_quant - old_quant

        if not db_order.status == OrderStatus.PENDING or not db_sale.status == SaleStatus.PENDIENTE:
            raise invalid_action("update detail")

        # Validar aumento
        if difference > 0:
            if db_menu_item.quant is not None and difference > db_menu_item.quant:
                raise invalid("quantity")

        # Actualizar inventario

        self.menu_item_service.update_item_quantity(
            db_menu_item, -difference)

        # Actualizar detalle
        db_order_detail.quantity = new_quant
        db_order_detail.subtotal = new_quant * db_order_detail.unit_price

        # Recalcular total
        self.order_service.update_order_totals(db_order)
        return self.order_service.to_public_order_details(self.order_service.save_order(db_order))

    def remove_order_detail(self, order_detail_id):
        db_order_detail = self.get_order_detail(order_detail_id)
        db_menu_item = db_order_detail.menu_item
        db_order = db_order_detail.order
        db_sale = db_order.sale

        if not db_order.status == OrderStatus.PENDING or not db_sale.status == SaleStatus.PENDIENTE:
            raise invalid_action("delete detail")

        if not db_menu_item or not db_order:
            raise not_found("Order or menu item")

        self.menu_item_service.update_item_quantity(
            db_menu_item,
            db_order_detail.quantity
        )

        db_order.order_details.remove(db_order_detail)
        self.order_service.update_order_totals(db_order)
        self.session.commit()


def get_order_detail_service(
    session: SessionDep,
    order_service: OrderServiceDep,
    menu_item_service: MenuItemServiceDep
) -> OrderDetailService:
    return OrderDetailService(session=session, order_service=order_service, menu_item_service=menu_item_service)


OrderItemServiceDep = Annotated[OrderDetailService,
                                Depends(get_order_detail_service)]
