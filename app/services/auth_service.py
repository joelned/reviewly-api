from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.models.user import User, UserRole, RefreshToken, hash_token
from app.models.profile import Profile
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_refresh_token_jwt,
    create_refresh_token,
    InvalidTokenError,
)

from app.config import settings


async def store_refresh_token(db: AsyncSession, user_id: int, token: str) -> None:
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    )

    db.add(record)


async def register_user(db: AsyncSession, data: RegisterRequest) -> dict:
    existing_email = await db.execute(select(User).where(User.email == data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    existing_username = await db.execute(
        select(User).where(User.username == data.username)
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")

    role = UserRole.REVIEWER if data.role == "reviewer" else UserRole.SUBMITTER
    user = User(
        email=data.email,
        username=data.username,
        password=data.password,
        role=role,
    )

    db.add(user)
    await db.flush()

    profile = Profile(user_id=user.id, display_name=user.username)
    db.add(profile)

    refresh_token = create_refresh_token(user.id)
    await store_refresh_token(db, user.id, refresh_token)

    await db.commit()
    await db.refresh(user)

    return {
        "access_token": create_access_token(user.id, user.role.value),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }
