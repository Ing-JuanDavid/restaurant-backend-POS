from app.database import Session, SessionDep
from sqlmodel import select
from app.utils.exceptions import not_found
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPublic
from fastapi import Depends, HTTPException, status
from typing import Annotated


class CustomerService():

    def __init__(self, session: Session):
        self.session = session

    def get_customers(self) -> list[CustomerPublic]:
        statment = select(Customer)
        return self.session.exec(statment).all()

    def create_customer(self, customer: CustomerCreate) -> CustomerPublic:

        db_customer = self.get_customer(customer.document)

        if db_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="customer already exist"
            )

        db_customer = Customer.model_validate(customer)

        self.session.add(db_customer)
        self.session.commit()
        self.session.refresh(db_customer)
        return db_customer

    def get_customer(self, document: int) -> Customer | None:
        db_customer = self.session.exec(select(Customer).where(
            Customer.document == document)).first()

        return db_customer

    def get_customer_document(self, document: int) -> Customer:
        db_customer = self.session.exec(select(Customer).where(
            Customer.document == document)).first()

        if not db_customer:
            raise not_found("Customer")

        return db_customer

    def update_customer(self, document: int, customer: CustomerUpdate):
        db_customer = self.get_customer_document(document)

        customer_data = customer.model_dump(exclude_unset=True)

        db_customer.sqlmodel_update(customer_data)
        self.session.commit()
        self.session.refresh(db_customer)
        return db_customer

    def delete_customer(self, document: int):
        db_customer = self.get_customer_document(document)

        self.session.delete(db_customer)
        self.session.commit()


def get_customer_service(
    session: SessionDep
):
    return CustomerService(session=session)


CustomerServiceDep = Annotated[
    CustomerService,
    Depends(get_customer_service)
]
