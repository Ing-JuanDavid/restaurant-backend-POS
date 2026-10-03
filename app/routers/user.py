from fastapi import APIRouter, Query, Depends
from app.models.user import UserRole, User
from app.dependencies.auth import authorize
from app.schemas.user import UserPublic
from app.services.user import UserServiceDep

router = APIRouter(prefix="/users", tags=["user"])


@router.get("", response_model=list[UserPublic])
async def get_users(
    service: UserServiceDep, role: UserRole | None = Query(default=None),
    user: User = Depends(authorize(UserRole.ADMIN))
):
    return service.get_users(role)
