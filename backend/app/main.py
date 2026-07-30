import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.endpoints import router
from app.core.config import settings
from app.api.deps import get_db

app = FastAPI(
    title=settings.APP_NAME,
    description="API de Consulta de Conciliações e Auditoria",
    version="1.0.0"
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

app.include_router(router, prefix="/api/v1")

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
