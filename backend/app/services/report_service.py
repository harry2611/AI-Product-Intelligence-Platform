from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_agents.insight_agent import InsightAgent
from app.models.analysis import FeatureRequest, InsightReport, SentimentResult, TopicMention
from app.models.feedback import Feedback


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.insight_agent = InsightAgent()

    def generate_weekly_report(self) -> InsightReport:
        period_end = datetime.now(UTC)
        period_start = period_end - timedelta(days=7)

        feedback_rows = self.db.execute(
            select(Feedback.id, Feedback.message)
            .where(Feedback.submitted_at >= period_start, Feedback.submitted_at <= period_end)
        ).all()

        if not feedback_rows:
            report = InsightReport(
                period_start=period_start,
                period_end=period_end,
                top_issues=[],
                top_feature_requests=[],
                recommendations=["No new feedback this week."],
                narrative="No feedback was ingested in the selected weekly period.",
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report

        negative_topics = self.db.execute(
            select(TopicMention.topic)
            .join(SentimentResult, SentimentResult.feedback_id == TopicMention.feedback_id)
            .join(Feedback, Feedback.id == TopicMention.feedback_id)
            .where(
                Feedback.submitted_at >= period_start,
                Feedback.submitted_at <= period_end,
                SentimentResult.label == "Negative",
            )
        ).scalars().all()

        feature_requests = self.db.execute(
            select(FeatureRequest.feature_name)
            .join(Feedback, Feedback.id == FeatureRequest.feedback_id)
            .where(Feedback.submitted_at >= period_start, Feedback.submitted_at <= period_end)
        ).scalars().all()

        top_negative = Counter(negative_topics).most_common(5)
        top_features = Counter(feature_requests).most_common(5)

        recommendations = self.insight_agent.generate_global_insights(
            top_negative_topics=top_negative,
            top_feature_requests=top_features,
        )

        narrative_lines = [
            "Weekly Product Intelligence Summary",
            "",
            "Top Issues:",
        ]
        for topic, count in top_negative:
            narrative_lines.append(f"- {topic}: {count} negative mentions")

        narrative_lines.append("")
        narrative_lines.append("Feature Requests:")
        for feature, count in top_features:
            narrative_lines.append(f"- {feature}: {count} requests")

        narrative_lines.append("")
        narrative_lines.append("Recommendations:")
        for recommendation in recommendations:
            narrative_lines.append(f"- {recommendation}")

        report = InsightReport(
            period_start=period_start,
            period_end=period_end,
            top_issues=[{"topic": topic, "count": count} for topic, count in top_negative],
            top_feature_requests=[{"feature_name": feature, "count": count} for feature, count in top_features],
            recommendations=recommendations,
            narrative="\n".join(narrative_lines),
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
