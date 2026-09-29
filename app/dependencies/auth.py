from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.models.token import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from app.services.user import UserService, UserServiceDep
from app.models.user import User, UserRole
from app.utils.exceptions import unauthorized


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_service: UserServiceDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def authorize(*roles: UserRole):
    async def role_checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not user.role in roles:
            raise unauthorized("rol")

        return user

    return role_checker
