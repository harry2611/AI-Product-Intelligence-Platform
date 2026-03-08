from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.analysis import InsightReport
from app.schemas.report import WeeklyReportResponse
from app.services.queue_service import enqueue_weekly_report_job

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/weekly/latest", response_model=WeeklyReportResponse)
def get_latest_weekly_report(db: Session = Depends(get_db)) -> InsightReport:
    report = db.scalar(select(InsightReport).where(InsightReport.report_type == "weekly").order_by(desc(InsightReport.id)))
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No weekly report available yet")
    return report


@router.post("/weekly/generate")
def generate_weekly_report() -> dict:
    job_id = enqueue_weekly_report_job()
    return {"message": "Weekly report generation queued", "job_id": job_id}
