
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session
from app.models.menu import *
from app.models.menu_item import *
from app.models.customer import *
from app.models.order_item import *
from app.config import settings


# engine creation
engine = create_engine(settings.database_url, echo=True)


# create tables.
# creates all of thouses wich have 'table = true'
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def init_data(session: Session):

    # menues
    desayuno = Menu(title='desayuno')
    almuerzos = Menu(title='almuerzos')
    bebidas = Menu(title="bebidas")
    session.add(desayuno)
    session.add(almuerzos)
    session.add(bebidas)
    session.commit()

    # categories
    # corrientes = Category(name="almuerzos")
    # bebidas = Category(name="bebidas")

    # session.add(corrientes)
    # session.add(bebidas)

    # session.commit()

    # adding itemns to breakfast menu
    huevos = MenuItem(
        name="huevos revueltos + yuca",
        price=6000,
        menu_id=desayuno.menu_id,
        status=True
    )

    chicharron = MenuItem(
        name="chicharron + yuca",
        price=12000,
        menu_id=desayuno.menu_id,
        status=True
    )

    cafe = MenuItem(
        name="cafe con leche",
        price="3000",
        menu_id=bebidas.menu_id,
        status=True
    )

    coca = MenuItem(
        menu_id=3,
        name="Coca cola",
        price=3500,
        quant=12,
        status=True
    )

    # adding items to luch menu

    cachama = MenuItem(
        name="cachama",
        price=20000,
        # category_id=corrientes.category_id,
        menu_id=almuerzos.menu_id,
        status=True
    )

    molida = MenuItem(
        name="Carne molida",
        price=12000,
        # category_id=corrientes.category_id,
        menu_id=almuerzos.menu_id,
        status=True
    )

    session.add(huevos)
    session.add(chicharron)
    session.add(cafe)
    session.add(coca)
    session.add(cachama)
    session.add(molida)
    session.commit()

    default_customer = Customer(
        customer_id=1,
        document=0,
        name="Consumidor",
        lastname="Final"
    )

    juan_cus = Customer(
        document=10645567889,
        name="Juan David",
        lastname="Salgado"
    )

    session.add(default_customer)
    session.commit()


def boostrapt_db():
    with Session(engine) as session:
        init_data(session)
