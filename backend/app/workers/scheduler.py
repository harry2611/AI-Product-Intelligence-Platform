import logging

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from app.core.config import settings

logger = logging.getLogger(__name__)


def enqueue_weekly_report() -> None:
    redis_conn = redis.from_url(settings.redis_url)
    queue = Queue(settings.worker_queue, connection=redis_conn)
    job = queue.enqueue("app.workers.tasks.generate_weekly_report_task", job_timeout=1200)
    logger.info("Scheduled weekly report job: %s", job.id)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        enqueue_weekly_report,
        trigger="cron",
        day_of_week=settings.weekly_report_day,
        hour=settings.weekly_report_hour,
        minute=settings.weekly_report_minute,
        id="weekly_product_report",
        replace_existing=True,
    )

    logger.info(
        "Scheduler started (weekly report: day=%s %02d:%02d UTC)",
        settings.weekly_report_day,
        settings.weekly_report_hour,
        settings.weekly_report_minute,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
