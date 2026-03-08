import redis
from rq import Connection, Worker

from app.core.config import settings


def main() -> None:
    redis_conn = redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        worker = Worker([settings.worker_queue])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
