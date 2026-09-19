from celery import Celery
from dotenv import load_dotenv
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
load_dotenv()
celery_app = Celery(
    "task_manager",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/2",
    include=["app.tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)