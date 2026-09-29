import jwt
from datetime import datetime, timezone, timedelta
from app.models.token import Token, SECRET_KEY, ALGORITHM
from app.config import settings


def create_access_token(data: dict) -> Token:
    to_encode = data.copy()
    exp_delta = timedelta(minutes=settings.jwt_token_expiration)

    expire = datetime.now(timezone.utc) + exp_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str: any]:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
