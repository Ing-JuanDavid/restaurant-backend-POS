from fastapi import APIRouter
from app.services.auth import AuthServiceDep
from app.schemas.user import UserRegister, AuthResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies.auth import authorize
from app.models.user import UserRole
from fastapi import Depends
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", response_model=AuthResponse)
async def register(register: UserRegister,  service: AuthServiceDep, user=Depends(authorize(UserRole.ADMIN))):
    return service.register(register)


@router.post("/login", tags=["auth"], response_model=AuthResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], sevice: AuthServiceDep):
    return sevice.login(form_data)
