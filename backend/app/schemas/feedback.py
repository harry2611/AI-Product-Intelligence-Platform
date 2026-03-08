from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    timestamp: datetime | None = None
    source: str = Field(default="manual", max_length=64)
    user_id: str = Field(default="anonymous", max_length=128)


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackBulkCreate(BaseModel):
    items: list[FeedbackCreate]


class FeedbackResponse(BaseModel):
    id: int
    message: str
    submitted_at: datetime
    source: str
    user_id: str
    processing_status: Literal["pending", "processed", "failed"]

    class Config:
        from_attributes = True


class FeedbackIngestResult(BaseModel):
    created_count: int
    queued_ids: list[int]
    message: str


class SentimentResultSchema(BaseModel):
    label: str
    score: float
    rationale: str | None = None


class FeedbackAnalysisDetail(BaseModel):
    feedback_id: int
    sentiment: SentimentResultSchema | None
    topics: list[str]
    feature_requests: list[str]
