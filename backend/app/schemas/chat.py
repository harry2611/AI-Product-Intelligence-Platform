from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=20)


class ChatCitation(BaseModel):
    feedback_id: int
    source: str
    user_id: str
    message: str
    score: float


class ChatQueryResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
