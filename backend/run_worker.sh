#!/bin/bash
echo "Iniciando worker do Celery..."
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=.
celery -A app.contexts.matching_auditing.worker worker --loglevel=info
