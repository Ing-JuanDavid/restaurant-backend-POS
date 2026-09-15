from fastapi import APIRouter
from app.security.auth import AuthServiceDep
from app.schemas.user import UserRegister, UserPublic, UserLoggin, LogginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", response_model=UserPublic)
async def register(register: UserRegister,  service: AuthServiceDep):
    return service.register(register)


@router.post("/loggin", tags=["auth"], response_model=LogginResponse)
async def loggin(loggin_data: UserLoggin, sevice: AuthServiceDep):
    return sevice.loggin(loggin_data)
