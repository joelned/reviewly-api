from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TimeStampMixin


class Profile(Base, TimeStampMixin):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    user: Mapped["User"] = relationship(back_populates="profile")  # type: ignore  # noqa: F821
    skills: Mapped[list["ReviewerSkills"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class ReviewerSkills(Base):
    __tablename__ = "reviewer_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)
    language: Mapped[str] = mapped_column(String(50))
    level: Mapped[str] = mapped_column(String(20))
    profile: Mapped["Profile"] = relationship(back_populates="skills")
