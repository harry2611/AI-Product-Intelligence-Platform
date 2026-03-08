from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.rate_limit import limiter
from app.rag.assistant import ProductIntelligenceAssistant
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse

router = APIRouter(prefix="/assistant", tags=["assistant"])
assistant = ProductIntelligenceAssistant()


@router.post("/query", response_model=ChatQueryResponse)
@limiter.limit(settings.rate_limit_per_minute)
def query_assistant(request: Request, payload: ChatQueryRequest) -> dict:
    return assistant.ask(question=payload.question, top_k=payload.top_k)
