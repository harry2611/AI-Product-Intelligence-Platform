from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SentimentResult(Base):
    __tablename__ = "sentiment_results"
    __table_args__ = (UniqueConstraint("feedback_id", name="uq_sentiment_feedback_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id", ondelete="CASCADE"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="sentiment_result")


class TopicMention(Base):
    __tablename__ = "topic_mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id", ondelete="CASCADE"), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="topic_mentions")


class FeatureRequest(Base):
    __tablename__ = "feature_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id", ondelete="CASCADE"), index=True, nullable=False)
    feature_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    normalized_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    request_text: Mapped[str] = mapped_column(Text, nullable=False)

    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="feature_requests")


class FeedbackEmbedding(Base):
    __tablename__ = "feedback_embeddings"
    __table_args__ = (UniqueConstraint("feedback_id", name="uq_embedding_feedback_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id", ondelete="CASCADE"), index=True, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="embedding")


class InsightReport(Base):
    __tablename__ = "insight_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_type: Mapped[str] = mapped_column(String(32), nullable=False, default="weekly")
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    top_issues: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    top_feature_requests: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    recommendations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
