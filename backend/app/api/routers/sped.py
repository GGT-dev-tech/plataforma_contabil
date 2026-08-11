import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_db
from app.models.obrigacoes import ObrigacaoAcessoriaJob, TipoObrigacao, StatusObrigacao
from app.tasks import gerar_sped_ecd_job

router = APIRouter(
    prefix="/sped",
    tags=["sped"]
)

class SpedRequest(BaseModel):
    empresa_id: str
    ano: str

@router.post("/ecd", status_code=202)
def request_sped_ecd(req: SpedRequest, db: Session = Depends(get_db)):
    """
    Enfileira a geração do SPED ECD via Celery (Background Job) e retorna o Job ID.
    """
    job = ObrigacaoAcessoriaJob(
        id=uuid.uuid4(),
        empresa_id=req.empresa_id,
        tipo=TipoObrigacao.SPED_ECD,
        ano_calendario=req.ano,
        status=StatusObrigacao.PENDENTE
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Enfileira tarefa no Celery
    gerar_sped_ecd_job.delay(str(job.id))
    
    return {"message": "Job enfileirado com sucesso", "job_id": str(job.id)}

@router.get("/status/{job_id}")
def check_sped_status(job_id: str, db: Session = Depends(get_db)):
    """
    Realiza o polling para checar se o arquivo foi gerado.
    """
    job = db.query(ObrigacaoAcessoriaJob).filter(ObrigacaoAcessoriaJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
        
    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "arquivo_url": job.arquivo_url,
        "log_erros": job.log_erros
    }
