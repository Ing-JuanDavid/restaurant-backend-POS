from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MESERO = "MESERO"
    CLIENTE = "CLIENTE"


class User(SQLModel, table=True):
    user_id: int | None = Field(primary_key=True, default=None)
    username: str = Field(min_length=10, max_length=50, unique=True)
    password_hash: str | None = None
    role: UserRole = UserRole.CLIENTE
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
