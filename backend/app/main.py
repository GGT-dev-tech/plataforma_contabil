import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.routers import workspaces
from app.contexts.identity.api import router as auth_router
from app.contexts.staging_ingestion.api_executions import router as staging_executions_router
from app.contexts.staging_ingestion.api_staging import router as staging_router
from app.contexts.matching_auditing.api_matching import router as matching_router
from app.contexts.obras.api_obras import router as obras_router
from app.contexts.obras.api_documentos_fiscais import router as documentos_fiscais_router
from app.api.routers.exportacao import router as exportacao_router
from app.api.routers.sincronizacao import router as sincronizacao_router
from app.api.routers.analytics import router as analytics_router
from app.core.config import settings
from app.api.deps import get_db

from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command
import os
@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(auth_router, prefix="/api/v1")
app.include_router(staging_executions_router, prefix="/api/v1")
app.include_router(staging_router, prefix="/api/v1")
app.include_router(matching_router, prefix="/api/v1")
app.include_router(workspaces.router, prefix="/api/v1")
app.include_router(obras_router, prefix="/api/v1")
app.include_router(documentos_fiscais_router, prefix="/api/v1")
app.include_router(exportacao_router, prefix="/api/v1")
app.include_router(sincronizacao_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

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
