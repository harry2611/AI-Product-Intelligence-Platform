from datetime import datetime

from pydantic import BaseModel


class WeeklyReportResponse(BaseModel):
    id: int
    period_start: datetime
    period_end: datetime
    top_issues: list
    top_feature_requests: list
    recommendations: list
    narrative: str
    created_at: datetime

    class Config:
        from_attributes = True
