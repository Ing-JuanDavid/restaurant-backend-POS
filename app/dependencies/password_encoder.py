from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("DUMMYPASSWORDsdjkefeoi3")


def get_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, password_hashed: str) -> bool:
    return password_hash.verify(plain_password, password_hashed)
