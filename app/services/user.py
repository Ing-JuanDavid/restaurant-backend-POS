from app.database import Session, SessionDep
from fastapi import Depends
from typing import Annotated
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserPublic
from app.utils.exceptions import invalid
from app.security import password_encoder
from sqlmodel import select


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        db_user = self.session.exec(statement).first()

        return db_user

    def create_user(self, user: UserCreate) -> User:
        db_user = User.model_validate(user)

        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def get_users(self, role: UserRole = None) -> list[UserPublic]:
        statemet = select(User)

        if role:
            statemet = statemet.where(User.role == role)

        users = self.session.exec(statemet).all()
        return users

    # create user controller


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
