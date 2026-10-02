from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt

from app.config import settings

password_hash=PasswordHash.recommended()


def hash_password(password : str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password,hashed_password)

def create_access_token(
    user_id: str,
    role: str
    ) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )