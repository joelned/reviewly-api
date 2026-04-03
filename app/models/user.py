from sqlalchemy import String, Boolean, Enum as SAEnum, ForeignKey, DateTime, func
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
    refresh_tokens: Mapped["RefreshToken"] = relationship(back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")  # Relationships


# Linter warnings appear because classes aren't directly imported in model files, but SQLAlchemy resolves them after all models load.

# TODO: implement these relationships at a later time
# submissions: Mapped[list["Submission"]] = relationship(back_populates="author")
# reviews: Mapped[list["Review"]] = relationship(back_populates="reviewer")
# notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
