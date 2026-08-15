from pydantic import BaseModel, Field
from app.models.sales import PaymentMethod
from datetime import datetime


class PaymentCreate(BaseModel):
    sale_id: int
    amount: int = Field(gt=0)
    method: PaymentMethod = PaymentMethod.EFECTIVO


class PaymentPublic(PaymentCreate):
    payment_id: int
    sale_id: int
    created_at: datetime


class PaymentUpdate(BaseModel):
    amount: int | None = Field(gt=0, default=None)
    method: PaymentMethod | None = None
