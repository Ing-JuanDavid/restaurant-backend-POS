
from app.dependencies import jwt
from app.models.user import User
from app.schemas.user import UserRegister, UserCreate, AuthResponse
from app.services.user import UserService, UserServiceDep, UserPublic
from sqlmodel import select
from app.utils.exceptions import invalid, unauthorized
from app.dependencies import password_encoder
from fastapi import Depends
from typing import Annotated
from app.utils.exceptions import invalid
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta


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

    # return a user

    def register(self, user_data: UserRegister) -> AuthResponse:
        user_exist = self.user_service.get_user_by_username(user_data.username)

        if user_exist:
            raise invalid("username")

        user_create = UserCreate(
            username=user_data.username,
            password_hash=password_encoder.get_hash(user_data.password),
            role=user_data.role,
            is_active=True
        )

        db_user = self.user_service.create_user(user_create)

        access_token = jwt.create_access_token(data={"sub": db_user.username})

        return self.to_auth_reponse(db_user, access_token)

    # return token data + user

    def login(self, form_data: OAuth2PasswordRequestForm) -> AuthResponse:

        db_user = self.authenticate(form_data.username, form_data.password)

        access_token = jwt.create_access_token(
            data={"sub": db_user.username}
        )

        return self.to_auth_reponse(db_user, access_token)

    def to_auth_reponse(self, db_user: User, access_token: str) -> AuthResponse:
        pub_user = UserPublic.model_validate(db_user)

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=pub_user
        )


def get_auth_service_dep(user_service: UserServiceDep) -> AuthService:
    return AuthService(user_service=user_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service_dep)]
