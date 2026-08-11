import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role

router = APIRouter(
    prefix="/sped",
    tags=["sped"]
)

class SpedRequest(BaseModel):
    ano: str

@router.post("/ecd", status_code=202)
def request_sped_ecd(
    req: SpedRequest, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enfileira a geração do SPED ECD via Celery (Background Job) e retorna o Job ID.
    """
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.sped.commands.request_sped_ecd import RequestSpedEcdCommandHandler
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Operação exige um tenant_id (empresa) válido.")
        
    try:
        with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
            return RequestSpedEcdCommandHandler.execute(uow, req.ano)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{job_id}")
def check_sped_status(
    job_id: str, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Realiza o polling para checar se o arquivo foi gerado.
    """
    from app.modules.sped.queries.get_sped_status import GetSpedStatusQueryHandler
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    result = GetSpedStatusQueryHandler.execute(db, tenant_id, job_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Job não encontrado ou não pertence à sua empresa")
        
    return result
