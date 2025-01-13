from celery import Celery

# Configure Celery with Redis as the broker
celery = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # Redis service from docker-compose
    backend="redis://redis:6379/0"
)

# Celery configuration
celery.conf.task_routes = {"tasks.index_document_task": {"queue": "indexing"}}