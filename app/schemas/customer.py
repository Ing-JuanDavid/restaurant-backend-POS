
from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    lastname: str | None = Field(max_length=50, default=None)
    cellphone: str | None = Field(max_length=20, default=None)
    address: str | None = None


class CustomerCreate(CustomerBase):
    document: int
    name: str = Field(max_length=50)


class CustomerUpdate(CustomerBase):
    document: int | None = None
    name: str | None = None


class CustomerPublic(CustomerBase):
    customer_id: int
    document: int
    name: str
