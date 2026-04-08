from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TimeStampMixin
import enum


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEW_REQUESTED = "review_requested"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Submission(Base, TimeStampMixin):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    code_content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(50))
    status: Mapped[SubmissionStatus] = mapped_column(
        SAEnum(SubmissionStatus), default=SubmissionStatus.PENDING
    )
    submitter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    submitter: Mapped["User"] = relationship(  # type: ignore # noqa: F821
        "User", foreign_keys=[submitter_id], back_populates="submissions"
    )

    reviewer: Mapped["User"] = relationship(  # type: ignore # noqa: F821
        "User", foreign_keys=[reviewer_id], back_populates="assigned_reviews"
    )


# Linter warnings appear because classes aren't directly imported in model files, but SQLAlchemy resolves them after all models load.
