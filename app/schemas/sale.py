from pydantic import BaseModel, Field
from app.models.sales import SaleStatus
from datetime import datetime


class SaleBase(BaseModel):
    status: SaleStatus | None = SaleStatus.PENDIENTE
    order_id: int


class SaleCreate(SaleBase):
    total: int = Field(gt=0)


class SalePublic(BaseModel):
    sale_id: int
    total: int
    status: SaleStatus
    order_id: int
    created_at: datetime
