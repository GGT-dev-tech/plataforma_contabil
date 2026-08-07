import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.routers import auth, executions, staging, matching
from app.core.config import settings
from app.api.deps import get_db

from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command
import os
from app.scripts_runner import run_startup_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa as migrations e popula o banco de forma automática e segura no Railway
    run_startup_tasks()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="API de Consulta de Conciliações e Auditoria",
    version="1.0.0",
    lifespan=lifespan
)

# Parse CORS origins
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    try:
        cors_origins = json.loads(cors_origins)
    except:
        cors_origins = [cors_origins]

# Adicionando CORS para o futuro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")
app.include_router(staging.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = "disconnected"
        
    return {
        "status": "ok",
        "database": db_status
    }
