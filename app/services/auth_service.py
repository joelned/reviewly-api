from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from app.models.user import User, UserRole, RefreshToken, hash_token
from app.models.profile import Profile
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.verification import create_verification_code, verify_verification_code
from app.services.email_service import EmailService
from app.config import settings
from app.schemas.auth import TokenResponse


async def store_refresh_token(db: AsyncSession, user_id: int, token: str) -> None:
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    )

    db.add(record)


async def register_user(
    db: AsyncSession, data: RegisterRequest, email_service: EmailService
) -> dict:
    existing_email = await db.execute(select(User).where(User.email == data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(400, "An account with this email already exists")

    existing_username = await db.execute(
        select(User).where(User.username == data.username)
    )

    if existing_username.scalar_one_or_none():
        raise HTTPException(400, "An account with this username already exists")

    user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role=UserRole.REVIEWER if data.role == "reviewer" else UserRole.SUBMITTER,
    )

    db.add(user)
    await db.flush()

    db.add(Profile(user_id=user.id, display_name=user.username))

    code = await create_verification_code(db, user.id)

    await db.commit()

    await email_service.send_verification_code(user.email, user.username, code)
    return {"message": "Account created. Check your email for a verification code"}


async def login(
    db: AsyncSession, login_request: LoginRequest, email_service: EmailService
) -> TokenResponse:

    existing = await db.execute(select(User).where(User.email == login_request.email))
    user = existing.scalar_one_or_none()

    if not user or not verify_password(login_request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been suspended")

    if not user.is_verified:
        code = await create_verification_code(db, user.id)
        await db.commit()
        await email_service.send_verification_code(user.email, user.username, code)
        raise HTTPException(
            status_code=403,
            detail="Your email address is not verified. A new code has been sent",
        )

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    await store_refresh_token(db, user.id, refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def verify_email(db: AsyncSession, email: str, code: str) -> TokenResponse:
    user = await verify_verification_code(db, email, code)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    await store_refresh_token(db, user.id, refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def resend_verification(
    db: AsyncSession, email: str, email_service: EmailService
) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=400, detail="No account was found with this email"
        )

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    code = await create_verification_code(db, user.id)
    await db.commit()

    await email_service.send_verification_code(user.email, user.username, code)

    return {"message": "A new verification code has been sent to your email"}
