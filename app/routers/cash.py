from fastapi import APIRouter, Query, Path
from app.models.cash import CashSession
from app.schemas.cash import CashDetailPublic, CashMovementPublic
from app.services.cash import CashSessionServiceDep
router = APIRouter(prefix="/cashs", tags=["cash"])


@router.post("/open", response_model=CashSession)
async def open_cash(service: CashSessionServiceDep, opening_balance: int | None = Query(ge=0, default=0)):
    return service.open_cash(opening_balance)


@router.post("/{cash_id}/close", response_model=CashDetailPublic)
async def close_cash(service: CashSessionServiceDep, cash_id: int, closing_balance: int = Query(gt=0)):
    return service.close_cash(cash_id, closing_balance)


@router.get("/{cash_id}/details", response_model=CashDetailPublic)
async def get_cash_details(service: CashSessionServiceDep, cash_id: int = Path(gt=0)):
    return service.get_cash_details(cash_id)


@router.get("/{cash_id}/movements", response_model=list[CashMovementPublic])
async def get_movements(service: CashSessionServiceDep, cash_id: int):
    return service.get_movements(cash_id)
