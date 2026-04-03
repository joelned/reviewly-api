from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from app.config import settings
import secrets
import hashlib


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    sub: str
    role: str
    token_type: str
    exp: str


class InvalidTokenError(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> str:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire
    )
    payload = {"sub": str(user_id), "role": role, "token_type": "access", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "token_type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    try:
        raw = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        payload = TokenPayload(**raw)
        if payload.token_type != "access":
            raise InvalidTokenError("Wrong token type")
        return payload
    except Exception:
        raise InvalidTokenError("Token invalid or expired")


def decode_refresh_token_jwt(token: str) -> dict:
    try:
        raw = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if raw.get("token_type") != "refresh":
            raise InvalidTokenError("Wrong token type")
        return raw
    except Exception:
        raise InvalidTokenError("Token invalid or expired")


def generate_6_digit_code() -> str:
    code = secrets.randbelow(900000) + 100000
    return str(code)


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def get_code_expiry(minutes: int = 15) -> datetime:
    datetime.now(timezone.utc) + timedelta(minutes=minutes)
