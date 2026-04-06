from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TimeStampMixin
from datetime import datetime
import hashlib
import enum


class UserRole(str, enum.Enum):
    SUBMITTER = "submitter"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(40), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.SUBMITTER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")  # type: ignore # noqa: F821
    verification_codes: Mapped[list["EmailVerificationCode"]] = relationship(
        back_populates="user"
    )
    password_reset_codes: Mapped[list["PasswordResetCode"]] = relationship(
        "PasswordResetCode", back_populates="user"
    )


# Linter warnings appear because classes aren't directly imported in model files, but SQLAlchemy resolves them after all models load.

# TODO: implement these relationships at a later time
# submissions: Mapped[list["Submission"]] = relationship(back_populates="author")
# reviews: Mapped[list["Review"]] = relationship(back_populates="reviewer")
# notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[bool] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="verification_codes")


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="password_reset_codes")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
