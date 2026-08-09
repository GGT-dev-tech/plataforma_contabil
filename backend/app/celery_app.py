from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import os

# Celery requires a broker (Redis is default for this setup)
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=False,
)

# Definir as tarefas agendadas (Cron jobs)
celery_app.conf.beat_schedule = {
    "sincronizacao-diaria-madrugada": {
        "task": "app.tasks.sincronizar_todas_empresas",
        # Roda todos os dias às 03:00 da manhã
        "schedule": crontab(hour=3, minute=0),
    },
}
