import hmac
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.user import User, EmailVerificationCode
from app.utils.security import generate_6_digit_code, get_code_expiry, hash_code

MAX_VERIFICATION_ATTEMPTS = 5


async def create_verification_code(db: AsyncSession, user_id: int) -> str:
    existing = await db.execute(
        select(EmailVerificationCode).where(
            and_(
                EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.used.is_(False),
            )
        )
    )
    for record in existing.scalars():
        await db.delete(record)

    code = generate_6_digit_code()
    db.add(
        EmailVerificationCode(
            user_id=user_id,
            code=hash_code(code),
            expires_at=get_code_expiry(minutes=15),
            used=False,
            attempts=0,
        )
    )

    await db.commit()
    return code


async def verify_verification_code(db: AsyncSession, email: str, code: str) -> User:

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or code")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    result = await db.execute(
        select(EmailVerificationCode).where(
            and_(
                EmailVerificationCode.user_id == user.id,
                EmailVerificationCode.used.is_(False),
            )
        )
    )
    code_record = result.scalar_one_or_none()

    if not code_record:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if code_record.expires_at < datetime.now(timezone.utc):
        await db.delete(code_record)
        raise HTTPException(status_code=400, detail="Code expired. Request a new one")

    if code_record.attempts >= MAX_VERIFICATION_ATTEMPTS:
        await db.delete(code_record)
        raise HTTPException(
            status_code=429, detail="Too many failed attempts. Request a new code."
        )

    if not hmac.compare_digest(hash_code(code), code_record.code):
        code_record.attempts += 1
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user.is_verified = True
    code_record.used = True
    await db.commit()
    await db.refresh(user)
    return user
