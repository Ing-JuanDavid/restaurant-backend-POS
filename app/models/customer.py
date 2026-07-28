from sqlmodel import SQLModel, Field, Relationship


class Customer(SQLModel, table=True):
    customer_id: int | None = Field(
        primary_key=True,
        default=None,
    )

    document: int = Field(unique=True, index=True)
    name: str = Field(max_length=50)
    lastname: str | None = Field(max_length=50, default=None)
    cellphone: str | None = Field(max_length=20, default=None)
    address: str | None = None

    orders: list["Order"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )
