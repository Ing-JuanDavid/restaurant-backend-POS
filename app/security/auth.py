
from app.models.user import User
from app.schemas.user import UserRegister, UserCreate, UserLoggin, LogginResponse
from app.services.user import UserService, UserServiceDep, UserPublic
from sqlmodel import select
from app.utils.exceptions import invalid, unauthorized
from app.security import password_encoder
from fastapi import Depends
from typing import Annotated
from app.utils.exceptions import invalid


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def authenticate(self, user_name: str, password: str) -> User:
        user = self.user_service.get_user_by_username(user_name)

        if not user:
            password_encoder.verify_password(
                password, password_encoder.DUMMY_HASH)
            raise unauthorized("credentials")

        if not password_encoder.verify_password(password, user.password_hash):
            raise unauthorized("credencials")

        if not user.is_active:
            raise unauthorized("user inactive")

        return user

    def register(self, user_data: UserRegister) -> UserPublic:
        user_exist = self.user_service.get_user_by_username(user_data.username)

        if user_exist:
            raise invalid("username")

        user_create = UserCreate(
            username=user_data.username,
            password_hash=password_encoder.get_hash(user_data.password),
            role=user_data.role,
            is_active=True
        )

        return self.user_service.create_user(user_create)

    # loggin function

    def loggin(self, login_data: UserLoggin) -> LogginResponse:

        user = UserPublic.model_validate(
            self.authenticate(login_data.username, login_data.password)
        )

        response = LogginResponse(
            token="",
            user=user
        )

        return response


def get_auth_service_dep(user_service: UserServiceDep) -> AuthService:
    return AuthService(user_service=user_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service_dep)]
