from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery("ekphrasis", broker=settings.redis_url, backend=settings.redis_url)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)

celery.conf.beat_schedule = {
    "refresh-top-stocks-nightly": {
        "task": "app.tasks.scrape_stocks.refresh_top_stocks",
        "schedule": crontab(hour=1, minute=0),
    },
}

celery.autodiscover_tasks(["app.tasks"])
