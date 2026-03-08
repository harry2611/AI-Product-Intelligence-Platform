from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="manual")
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    sentiment_result: Mapped["SentimentResult | None"] = relationship(
        "SentimentResult",
        back_populates="feedback",
        uselist=False,
        cascade="all, delete-orphan",
    )
    topic_mentions: Mapped[list["TopicMention"]] = relationship(
        "TopicMention",
        back_populates="feedback",
        cascade="all, delete-orphan",
    )
    feature_requests: Mapped[list["FeatureRequest"]] = relationship(
        "FeatureRequest",
        back_populates="feedback",
        cascade="all, delete-orphan",
    )
    embedding: Mapped["FeedbackEmbedding | None"] = relationship(
        "FeedbackEmbedding",
        back_populates="feedback",
        uselist=False,
        cascade="all, delete-orphan",
    )
