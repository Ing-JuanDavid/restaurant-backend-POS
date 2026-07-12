from fastapi import APIRouter, HTTPException, status

from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPublic
from app.services.customer import CustomerServiceDep


router = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


@router.get("", response_model=list[CustomerPublic])
async def read_customers(service: CustomerServiceDep):
    customers = service.get_customers()
    return customers


@router.post("", response_model=CustomerPublic, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, service: CustomerServiceDep):
    db_customer = service.create_customer(
        customer
    )
    return db_customer


@router.get("/{document}", response_model=CustomerPublic)
async def read_customer_document(document: int, service: CustomerServiceDep):
    db_customer = service.get_customer(document)

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="customer not found"
        )

    return db_customer


@router.put("/{document}", response_model=CustomerPublic)
async def update_customer(document: int, customer: CustomerUpdate, service: CustomerServiceDep):
    db_customer = service.update_customer(document, customer)
    return db_customer


@router.delete("/{document}")
async def delete_customer(document: int, service: CustomerServiceDep):
    service.delete_customer(document)
    return {"messaje": "ok"}
