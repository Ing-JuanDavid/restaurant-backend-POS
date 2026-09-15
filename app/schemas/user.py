from pydantic import BaseModel, Field, ConfigDict
from app.models.user import UserRole


class UserLoggin(BaseModel):
    username: str
    password: str


class LogginResponse(BaseModel):
    token: str
    user: UserPublic


class UserRegister(BaseModel):
    username: str = Field(min_length=10, max_length=50)
    password: str
    role: UserRole = UserRole.CLIENTE


class UserCreate(BaseModel):
    username: str = Field(min_length=10, max_length=50)
    password_hash: str
    role: UserRole = UserRole.CLIENTE
    is_active: bool = True


class UserPublic(BaseModel):
    username: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
