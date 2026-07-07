from sqlmodel import SQLModel, Field, Relationship


class BaseCustomer(SQLModel):
    document: int = Field(unique=True, index=True)
    name: str = Field(max_length=50)
    lastname: str | None = Field(max_length=50, default=None)
    phone: str | None = Field(max_length=20, default=None)
    address: str | None = None


class Customer(BaseCustomer, table=True):
    customer_id: int | None = Field(
        primary_key=True,
        default=None,
    )

    orders: list["Order"] = Relationship(
        back_populates="customer", cascade_delete=True)


class UpdateCustomer(SQLModel):
    document: int | None = None
    name: str | None = None
    lastname: str | None = None
    phone: str | None = None
    address: str | None = None


class PublicCustomer(BaseCustomer):
    customer_id: int
