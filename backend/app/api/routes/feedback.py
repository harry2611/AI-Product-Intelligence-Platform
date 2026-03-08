import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.models.analysis import FeatureRequest, SentimentResult, TopicMention
from app.models.feedback import Feedback
from app.schemas.feedback import (
    FeedbackAnalysisDetail,
    FeedbackBulkCreate,
    FeedbackCreate,
    FeedbackIngestResult,
    FeedbackResponse,
    SentimentResultSchema,
)
from app.services.feedback_service import create_feedback, create_feedback_bulk
from app.services.queue_service import enqueue_feedback_job

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/manual", response_model=FeedbackIngestResult)
@limiter.limit(settings.rate_limit_per_minute)
def ingest_manual_feedback(
    request: Request, payload: FeedbackCreate, db: Session = Depends(get_db)
) -> FeedbackIngestResult:
    feedback = create_feedback(db, payload)
    db.commit()
    enqueue_feedback_job(feedback.id)
    return FeedbackIngestResult(created_count=1, queued_ids=[feedback.id], message="Feedback queued for AI processing")


@router.post("/bulk", response_model=FeedbackIngestResult)
@limiter.limit(settings.rate_limit_per_minute)
def ingest_bulk_feedback(
    request: Request, payload: FeedbackBulkCreate, db: Session = Depends(get_db)
) -> FeedbackIngestResult:
    feedbacks = create_feedback_bulk(db, payload.items)
    db.commit()
    queued_ids = []
    for item in feedbacks:
        enqueue_feedback_job(item.id)
        queued_ids.append(item.id)
    return FeedbackIngestResult(
        created_count=len(feedbacks),
        queued_ids=queued_ids,
        message="Bulk feedback queued for AI processing",
    )


@router.post("/upload/csv", response_model=FeedbackIngestResult)
@limiter.limit(settings.rate_limit_per_minute)
async def upload_csv_feedback(
    request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> FeedbackIngestResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a .csv file")

    content = await file.read()
    text_content = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text_content))

    items: list[FeedbackCreate] = []
    for row in reader:
        if not row.get("message"):
            continue
        timestamp = row.get("timestamp")
        parsed_timestamp = None
        if timestamp:
            try:
                parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid timestamp format in CSV row: {timestamp}",
                ) from exc
        items.append(
            FeedbackCreate(
                message=row["message"],
                source=row.get("source") or "csv",
                user_id=row.get("user_id") or "csv_import",
                timestamp=parsed_timestamp,
            )
        )

    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV did not contain valid feedback rows")

    feedbacks = create_feedback_bulk(db, items)
    db.commit()
    queued_ids = []
    for item in feedbacks:
        enqueue_feedback_job(item.id)
        queued_ids.append(item.id)

    return FeedbackIngestResult(
        created_count=len(feedbacks),
        queued_ids=queued_ids,
        message="CSV feedback queued for AI processing",
    )


@router.post("/upload/json", response_model=FeedbackIngestResult)
@limiter.limit(settings.rate_limit_per_minute)
async def upload_json_feedback(
    request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> FeedbackIngestResult:
    if not file.filename or not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a .json file")

    content = await file.read()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON file") from exc

    if not isinstance(payload, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JSON upload expects an array of feedback items")

    items: list[FeedbackCreate] = []
    for row in payload:
        if not isinstance(row, dict) or "message" not in row:
            continue
        items.append(FeedbackCreate(**row))

    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid feedback entries found in JSON file")

    feedbacks = create_feedback_bulk(db, items)
    db.commit()
    queued_ids = []
    for item in feedbacks:
        enqueue_feedback_job(item.id)
        queued_ids.append(item.id)

    return FeedbackIngestResult(
        created_count=len(feedbacks),
        queued_ids=queued_ids,
        message="JSON feedback queued for AI processing",
    )


@router.get("", response_model=list[FeedbackResponse])
def list_feedback(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Feedback]:
    rows = db.execute(select(Feedback).order_by(Feedback.submitted_at.desc()).limit(limit).offset(offset)).scalars().all()
    return rows


@router.get("/{feedback_id}/analysis", response_model=FeedbackAnalysisDetail)
def get_feedback_analysis(feedback_id: int, db: Session = Depends(get_db)) -> FeedbackAnalysisDetail:
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    sentiment = db.scalar(select(SentimentResult).where(SentimentResult.feedback_id == feedback_id))
    topics = db.execute(select(TopicMention.topic).where(TopicMention.feedback_id == feedback_id)).scalars().all()
    features = db.execute(select(FeatureRequest.feature_name).where(FeatureRequest.feedback_id == feedback_id)).scalars().all()

    sentiment_schema = None
    if sentiment:
        sentiment_schema = SentimentResultSchema(label=sentiment.label, score=sentiment.score, rationale=sentiment.rationale)

    return FeedbackAnalysisDetail(
        feedback_id=feedback_id,
        sentiment=sentiment_schema,
        topics=list(topics),
        feature_requests=list(features),
    )
