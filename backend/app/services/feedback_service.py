from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate


def create_feedback(db: Session, payload: FeedbackCreate) -> Feedback:
    submitted_at = payload.timestamp or datetime.now(timezone.utc)
    feedback = Feedback(
        message=payload.message,
        submitted_at=submitted_at,
        source=payload.source,
        user_id=payload.user_id,
        processing_status="pending",
    )
    db.add(feedback)
    db.flush()
    return feedback


def create_feedback_bulk(db: Session, payloads: Iterable[FeedbackCreate]) -> list[Feedback]:
    created: list[Feedback] = []
    for payload in payloads:
        created.append(create_feedback(db, payload))
    return created
