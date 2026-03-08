from __future__ import annotations

import redis
from rq import Queue

from app.core.config import settings


_redis_client = redis.from_url(settings.redis_url)
_queue = Queue(settings.worker_queue, connection=_redis_client)


def enqueue_feedback_job(feedback_id: int) -> str:
    job = _queue.enqueue("app.workers.tasks.process_feedback_task", feedback_id, job_timeout=600)
    return job.id


def enqueue_weekly_report_job() -> str:
    job = _queue.enqueue("app.workers.tasks.generate_weekly_report_task", job_timeout=1200)
    return job.id


def publish_event(payload: str) -> None:
    _redis_client.publish(settings.feedback_event_channel, payload)
