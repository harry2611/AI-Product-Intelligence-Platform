from fastapi import APIRouter

from app.api.routes import analytics, assistant, auth, feedback, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)
api_router.include_router(assistant.router)
api_router.include_router(reports.router)
