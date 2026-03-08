import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import api_router
from app.api.routes.websocket import router as websocket_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.db.init_db import init_db
from app.services.realtime import redis_listener

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    redis_task = asyncio.create_task(redis_listener())
    try:
        yield
    finally:
        redis_task.cancel()
        await asyncio.gather(redis_task, return_exceptions=True)


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(websocket_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
