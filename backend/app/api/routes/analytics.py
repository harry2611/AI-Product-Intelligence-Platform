from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.analytics import AnalyticsSummary, FeatureRequestCountItem, TopicCountItem, TrendPoint
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).summary(days=days)


@router.get("/trends", response_model=list[TrendPoint])
def get_trends(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)) -> list[dict]:
    return AnalyticsService(db).sentiment_trends(days=days)


@router.get("/feature-requests", response_model=list[FeatureRequestCountItem])
def get_feature_requests(
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    return AnalyticsService(db).feature_request_frequency(days=days, limit=limit)


@router.get("/top-complaints", response_model=list[TopicCountItem])
def get_top_complaints(
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    return AnalyticsService(db).top_complaints(days=days, limit=limit)
