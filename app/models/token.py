from pydantic import BaseModel


# openssl rand -hex 32
SECRET_KEY = "e13e0f6fca3c8ecb0e2bdd340e8e0bb9184e422b940a8f1a5578d22a38677657"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


class Token(BaseModel):
    token_type: str
    token: str
