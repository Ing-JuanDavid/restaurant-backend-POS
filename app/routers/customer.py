from fastapi import APIRouter, HTTPException, status

from app.models.customer import *
from app.database import SessionDep
from app.services.customer import CustomerServiceDep
from sqlmodel import select

router = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


@router.get("", response_model=list[PublicCustomer])
async def read_customers(session: SessionDep):
    customers = session.exec(select(Customer)).all()
    return customers


@router.post("", response_model=PublicCustomer)
async def create_customer(customer: BaseCustomer, service: CustomerServiceDep):
    db_customer = service.create_customer(
        customer=customer
    )
    return db_customer


@router.get("/{document}", response_model=PublicCustomer)
async def read_customer_document(document: int, service: CustomerServiceDep):
    db_customer = service.get_customer(document=document)

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="customer not found"
        )

    return db_customer


@router.put("/{document}", response_model=PublicCustomer)
async def update_customer(document: int, customer: UpdateCustomer, service: CustomerServiceDep):
    db_customer = service.update_customer(document, customer)
    return db_customer


@router.delete("/{document}")
async def delete_customer(document: int, service: CustomerServiceDep):
    service.delete_customer(document)
    return {"messaje": "ok"}
