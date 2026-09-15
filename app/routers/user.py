from fastapi import APIRouter, Query
from app.models.user import UserRole
from app.schemas.user import UserPublic
from app.services.user import UserServiceDep

router = APIRouter(prefix="/users", tags=["user"])


@router.get("", response_model=list[UserPublic])
async def get_users(service: UserServiceDep, role: UserRole | None = Query(default=None)):
    return service.get_users(role)
