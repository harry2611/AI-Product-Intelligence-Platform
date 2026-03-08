from __future__ import annotations

import json
import logging

from sqlalchemy import select

from app.ai_agents.orchestrator import AgentOrchestrator
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.analysis import FeedbackEmbedding, FeatureRequest, SentimentResult, TopicMention
from app.models.feedback import Feedback
from app.services.embedding_service import get_embedding_service
from app.services.queue_service import publish_event
from app.services.report_service import ReportService
from app.vector_db.chroma_client import get_chroma_store

logger = logging.getLogger(__name__)

orchestrator = AgentOrchestrator()
embedding_service = get_embedding_service()
chroma_store = get_chroma_store()


def process_feedback_task(feedback_id: int) -> None:
    db = SessionLocal()
    try:
        feedback = db.get(Feedback, feedback_id)
        if not feedback:
            logger.warning("Feedback %s not found", feedback_id)
            return

        analysis = orchestrator.analyze_feedback(feedback.message)

        _upsert_sentiment(db=db, feedback=feedback, sentiment=analysis["sentiment"])
        _replace_topics(db=db, feedback=feedback, topics=analysis["topics"])
        _replace_feature_requests(db=db, feedback=feedback, feature_requests=analysis["feature_requests"])

        embedding = embedding_service.embed_text(feedback.message)
        vector_id = chroma_store.upsert_feedback(
            feedback_id=feedback.id,
            message=feedback.message,
            embedding=embedding,
            metadata={
                "source": feedback.source,
                "user_id": feedback.user_id,
                "submitted_at": feedback.submitted_at.isoformat(),
                "sentiment": analysis["sentiment"]["label"],
                "topics": [topic["topic"] for topic in analysis["topics"]],
            },
        )

        _upsert_embedding(db=db, feedback=feedback, vector_id=vector_id, dimensions=len(embedding))

        feedback.processing_status = "processed"
        feedback.error_message = None
        db.commit()

        payload = {
            "event": "feedback_processed",
            "feedback_id": feedback.id,
            "source": feedback.source,
            "user_id": feedback.user_id,
            "sentiment": analysis["sentiment"]["label"],
            "topics": [topic["topic"] for topic in analysis["topics"]],
            "insight": analysis["insight"],
        }
        publish_event(json.dumps(payload))
    except Exception as exc:
        logger.exception("Failed processing feedback %s: %s", feedback_id, exc)
        feedback = db.get(Feedback, feedback_id)
        if feedback:
            feedback.processing_status = "failed"
            feedback.error_message = str(exc)
            db.commit()
        publish_event(
            json.dumps(
                {
                    "event": "feedback_failed",
                    "feedback_id": feedback_id,
                    "error": str(exc),
                }
            )
        )
    finally:
        db.close()


def generate_weekly_report_task() -> None:
    db = SessionLocal()
    try:
        report = ReportService(db).generate_weekly_report()
        publish_event(
            json.dumps(
                {
                    "event": "weekly_report_generated",
                    "report_id": report.id,
                    "period_start": report.period_start.isoformat(),
                    "period_end": report.period_end.isoformat(),
                }
            )
        )
    finally:
        db.close()


def _upsert_sentiment(db, feedback: Feedback, sentiment: dict) -> None:
    record = db.scalar(select(SentimentResult).where(SentimentResult.feedback_id == feedback.id))
    if not record:
        record = SentimentResult(feedback_id=feedback.id, label="Neutral", score=0.5, rationale="")
        db.add(record)

    record.label = sentiment["label"]
    record.score = float(sentiment["score"])
    record.rationale = sentiment.get("rationale", "")


def _replace_topics(db, feedback: Feedback, topics: list[dict]) -> None:
    db.query(TopicMention).filter(TopicMention.feedback_id == feedback.id).delete()
    for topic in topics:
        db.add(
            TopicMention(
                feedback_id=feedback.id,
                topic=topic["topic"],
                confidence=float(topic.get("confidence", 0.5)),
            )
        )


def _replace_feature_requests(db, feedback: Feedback, feature_requests: list[dict]) -> None:
    db.query(FeatureRequest).filter(FeatureRequest.feedback_id == feedback.id).delete()
    for request in feature_requests:
        db.add(
            FeatureRequest(
                feedback_id=feedback.id,
                feature_name=request["feature_name"],
                normalized_key=request["normalized_key"],
                request_text=request["request_text"],
            )
        )


def _upsert_embedding(db, feedback: Feedback, vector_id: str, dimensions: int) -> None:
    record = db.scalar(select(FeedbackEmbedding).where(FeedbackEmbedding.feedback_id == feedback.id))
    if not record:
        record = FeedbackEmbedding(
            feedback_id=feedback.id,
            vector_id=vector_id,
            model_name=settings.embedding_model_name,
            dimensions=dimensions,
            vector_metadata={},
        )
        db.add(record)

    record.vector_id = vector_id
    record.model_name = settings.embedding_model_name
    record.dimensions = dimensions
    record.vector_metadata = {"status": "indexed"}
