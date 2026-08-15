from fastapi import APIRouter, Query, Path
from typing import Annotated
from app.schemas.sale import SalePublic, SaleSummary
from app.schemas.payment import PaymentCreate, PaymentPublic, PaymentUpdate
from app.models.sales import SaleStatus
from app.services.sales import SalesServiceDep
from app.services.payment import PaymentServiceDep

router = APIRouter(prefix="/sales", tags=["sale"])


@router.get("", response_model=list[SalePublic])
async def get_sales(
        service: SalesServiceDep,
        sale_status: SaleStatus | None = None):
    return service.get_sales(sale_status)


@router.get("/{sale_id}", response_model=SaleSummary)
async def get_sale(sale_id: int, service: SalesServiceDep):
    return service.get_summary_sale(sale_id)


@router.post("/payments", response_model=SaleSummary)
async def create_payment(payment: PaymentCreate, service: PaymentServiceDep):
    return service.create_payment(payment)


@router.get("{sale_id}/payments", response_model=list[PaymentPublic])
async def get_payments_sale(service: PaymentServiceDep, sale_id: int = Path(gt=0)):
    return service.get_payments_by_sale(sale_id)


@router.patch("/payments/{payment_id}", response_model=SaleSummary)
async def update_payment(payment_id: int, payment: PaymentUpdate, service: PaymentServiceDep):
    return service.update_payment(payment_id, payment)
