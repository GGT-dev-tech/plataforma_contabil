FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 (if needed) and curl for healthcheck
RUN apt-get update && apt-get install -y libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "python3 app/scripts_runner.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
