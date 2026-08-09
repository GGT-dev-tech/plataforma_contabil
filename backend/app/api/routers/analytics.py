from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.api.deps import get_db
from app.contexts.analytics.service import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    empresa_id: str = "32ecbd0c-25d2-43bb-a30f-b1eaf602ed05", # Default hardcoded for MVP
    db: Session = Depends(get_db)
):
    """
    Retorna todos os dados consolidados para o Dashboard em uma única chamada.
    """
    service = AnalyticsService(db)
    
    return service.get_dashboard_geral(empresa_id)
