import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.api.deps import get_db
from fastapi.responses import StreamingResponse
from datetime import datetime, date
from io import StringIO
from app.models.domain import Usuario, Role
from app.contexts.identity.auth_utils import get_current_user
from app.contexts.tax_sped.engine import SpedEcdGenerator

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

@router.get("/ecd/{empresa_id}/download")
def download_sped_ecd(
    empresa_id: str,
    data_inicio: date,
    data_fim: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera e faz o download direto do SPED ECD em formato .txt (Bloco 0 e I).
    Para grandes volumes recomenda-se usar a geração assíncrona.
    """
    if current_user.role != "ADMIN" and str(current_user.empresa_id) != empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    try:
        generator = SpedEcdGenerator(
            db=db,
            empresa_id=empresa_id,
            data_inicio=datetime.combine(data_inicio, datetime.min.time()),
            data_fim=datetime.combine(data_fim, datetime.max.time())
        )
        
        txt_content = generator.exportar()
        
        # Converte para file-like object para StreamingResponse
        file_stream = StringIO(txt_content)
        
        filename = f"SPED_ECD_{empresa_id}_{data_inicio.strftime('%Y%m')}.txt"
        
        return StreamingResponse(
            iter([file_stream.getvalue()]), 
            media_type="text/plain", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar SPED: {str(e)}")
