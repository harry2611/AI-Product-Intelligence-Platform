from datetime import date

from pydantic import BaseModel


class SentimentDistributionItem(BaseModel):
    label: str
    count: int
    percentage: float


class TopicCountItem(BaseModel):
    topic: str
    count: int


class FeatureRequestCountItem(BaseModel):
    feature_name: str
    count: int


class TrendPoint(BaseModel):
    day: date
    total_feedback: int
    negative_feedback: int


class AnalyticsSummary(BaseModel):
    total_feedback: int
    processed_feedback: int
    pending_feedback: int
    sentiment_distribution: list[SentimentDistributionItem]
    top_topics: list[TopicCountItem]
    top_feature_requests: list[FeatureRequestCountItem]
