from celery import Celery
from dotenv import load_dotenv
from app.core.logging import setup_logging

setup_logging()
load_dotenv()
celery_app = Celery(
    "task_manager",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
    include=["app.tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)