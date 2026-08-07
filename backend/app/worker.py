import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="run_pipeline_task")
def run_pipeline_task(execucao_id: str):
    from app.pipeline.runner import execute_pipeline_core
    from app.api.deps import SessionLocal
    
    db = SessionLocal()
    try:
        execute_pipeline_core(execucao_id, db)
    finally:
        db.close()
