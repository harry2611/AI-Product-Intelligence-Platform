from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.analysis import FeatureRequest, SentimentResult, TopicMention
from app.models.feedback import Feedback


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self, days: int = 30) -> dict:
        since = datetime.now(UTC) - timedelta(days=days)

        total_feedback = self.db.scalar(select(func.count(Feedback.id)).where(Feedback.submitted_at >= since)) or 0
        processed_feedback = (
            self.db.scalar(
                select(func.count(Feedback.id)).where(Feedback.submitted_at >= since, Feedback.processing_status == "processed")
            )
            or 0
        )
        pending_feedback = (
            self.db.scalar(
                select(func.count(Feedback.id)).where(Feedback.submitted_at >= since, Feedback.processing_status == "pending")
            )
            or 0
        )

        sentiment_rows = self.db.execute(
            select(SentimentResult.label, func.count(SentimentResult.id))
            .join(Feedback, Feedback.id == SentimentResult.feedback_id)
            .where(Feedback.submitted_at >= since)
            .group_by(SentimentResult.label)
        ).all()

        sentiments = []
        for label, count in sentiment_rows:
            percentage = (count / processed_feedback * 100) if processed_feedback else 0.0
            sentiments.append({"label": label, "count": int(count), "percentage": round(percentage, 2)})

        topic_rows = self.db.execute(
            select(TopicMention.topic, func.count(TopicMention.id))
            .join(Feedback, Feedback.id == TopicMention.feedback_id)
            .where(Feedback.submitted_at >= since)
            .group_by(TopicMention.topic)
            .order_by(func.count(TopicMention.id).desc())
            .limit(10)
        ).all()

        feature_rows = self.db.execute(
            select(FeatureRequest.feature_name, func.count(FeatureRequest.id))
            .join(Feedback, Feedback.id == FeatureRequest.feedback_id)
            .where(Feedback.submitted_at >= since)
            .group_by(FeatureRequest.feature_name)
            .order_by(func.count(FeatureRequest.id).desc())
            .limit(10)
        ).all()

        return {
            "total_feedback": int(total_feedback),
            "processed_feedback": int(processed_feedback),
            "pending_feedback": int(pending_feedback),
            "sentiment_distribution": sentiments,
            "top_topics": [{"topic": row[0], "count": int(row[1])} for row in topic_rows],
            "top_feature_requests": [{"feature_name": row[0], "count": int(row[1])} for row in feature_rows],
        }

    def sentiment_trends(self, days: int = 30) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=days)

        rows = self.db.execute(
            select(
                func.date(Feedback.submitted_at).label("day"),
                func.count(Feedback.id).label("total"),
                func.sum(case((SentimentResult.label == "Negative", 1), else_=0)).label("negative"),
            )
            .join(SentimentResult, SentimentResult.feedback_id == Feedback.id, isouter=True)
            .where(Feedback.submitted_at >= since)
            .group_by(func.date(Feedback.submitted_at))
            .order_by(func.date(Feedback.submitted_at))
        ).all()

        return [
            {
                "day": row.day if isinstance(row.day, date) else row[0],
                "total_feedback": int(row.total or 0),
                "negative_feedback": int(row.negative or 0),
            }
            for row in rows
        ]

    def feature_request_frequency(self, days: int = 30, limit: int = 20) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=days)
        rows = self.db.execute(
            select(FeatureRequest.feature_name, func.count(FeatureRequest.id))
            .join(Feedback, Feedback.id == FeatureRequest.feedback_id)
            .where(Feedback.submitted_at >= since)
            .group_by(FeatureRequest.feature_name)
            .order_by(func.count(FeatureRequest.id).desc())
            .limit(limit)
        ).all()
        return [{"feature_name": row[0], "count": int(row[1])} for row in rows]

    def top_complaints(self, days: int = 30, limit: int = 10) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=days)

        rows = self.db.execute(
            select(TopicMention.topic, func.count(TopicMention.id))
            .join(Feedback, Feedback.id == TopicMention.feedback_id)
            .join(SentimentResult, SentimentResult.feedback_id == Feedback.id)
            .where(Feedback.submitted_at >= since, SentimentResult.label == "Negative")
            .group_by(TopicMention.topic)
            .order_by(func.count(TopicMention.id).desc())
            .limit(limit)
        ).all()
        return [{"topic": row[0], "count": int(row[1])} for row in rows]
