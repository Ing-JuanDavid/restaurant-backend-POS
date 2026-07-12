from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import menu, customer, menu_item, order
from app.database import create_db_and_tables, boostrapt_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # boostrapt_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(menu.router)
# app.include_router(category.router)
app.include_router(menu_item.router)

app.include_router(customer.router)

app.include_router(order.router)


@app.get("/")
async def hello():
    return {
        "message": "hello world"
    }
