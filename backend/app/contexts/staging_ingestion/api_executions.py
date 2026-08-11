import uuid
import json
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api import schemas
from app.contexts.identity.auth_utils import get_current_user
from app.api.deps import get_db
from app.models.domain import Usuario, Role, ExecucaoPipeline, StatusExecucao, ImportacaoArquivo, TipoArquivo
from app.core.uow import SQLAlchemyUnitOfWork
from app.services.storage import LocalStorageProvider
from app.contexts.matching_auditing.pipeline.runner import CeleryRunner

router = APIRouter(prefix="/executions", tags=["executions"])

@router.get("")
def list_executions(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        query = uow.session.query(ExecucaoPipeline)
        if current_user.role != Role.ADMIN:
            query = query.filter(ExecucaoPipeline.empresa_id == current_user.empresa_id)
            
        execs = query.order_by(ExecucaoPipeline.data_inicio.desc()).limit(100).all()
        return [{
            "id": e.id,
            "status": e.status.name,
            "data_inicio": e.data_inicio,
            "data_fim": e.data_fim
        } for e in execs]

@router.get("/{exec_id}")
def get_execution(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        e = uow.executions.get(uow.session, exec_id)
        if not e: raise HTTPException(status_code=404, detail="Não encontrado")
        if current_user.role != Role.ADMIN and e.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado a dados de outra empresa (Multi-Tenant).")
        return {
            "id": e.id,
            "status": e.status.name,
            "data_inicio": e.data_inicio,
            "data_fim": e.data_fim,
            "matching_profile": e.matching_profile
        }

class CreateExecutionRequest(schemas.BaseModel):
    empresa_id: str = None

@router.post("", response_model=schemas.ExecucaoPipelineSchema)
def create_execution(payload: CreateExecutionRequest = None, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403, detail="Permissão negada")
        
    empresa_selecionada = current_user.empresa_id
    if payload and payload.empresa_id:
        if current_user.role == Role.ADMIN or str(current_user.empresa_id) == payload.empresa_id:
            empresa_selecionada = payload.empresa_id
        else:
            raise HTTPException(status_code=403, detail="Acesso negado ao Workspace selecionado.")
    
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = ExecucaoPipeline(
            id=str(uuid.uuid4()), 
            empresa_id=empresa_selecionada,
            status=StatusExecucao.CRIADA, 
            matching_profile="financeiro_2026", 
            runtime_profile="api"
        )
        uow.session.add(execucao)
        uow.commit()
        uow.session.refresh(execucao)
        return execucao

@router.post("/{exec_id}/files", status_code=202)
def upload_files(exec_id: str, despesas: UploadFile = File(...), razao: UploadFile = File(...), extrato: UploadFile = File(...), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    storage = LocalStorageProvider()
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404)
        if current_user.role != Role.ADMIN and execucao.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado a dados de outra empresa (Multi-Tenant).")
        
        def save_and_hash(file_upload, tipo):
            content = file_upload.file.read()
            file_upload.file.seek(0)
            sha256 = hashlib.sha256(content).hexdigest()
            tamanho = len(content)
            path = storage.save(exec_id, file_upload.filename, file_upload.file)
            arquivo = ImportacaoArquivo(id=str(uuid.uuid4()), execucao_id=exec_id, nome_original=file_upload.filename, tipo=tipo, storage_path=path, hash_sha256=sha256, tamanho_bytes=tamanho, uploaded_by=current_user.id)
            uow.session.add(arquivo)
            return file_upload.filename
            
        f_desp = save_and_hash(despesas, TipoArquivo.DESPESA)
        f_raz = save_and_hash(razao, TipoArquivo.RAZAO)
        f_ext = save_and_hash(extrato, TipoArquivo.EXTRATO)
        
        execucao.status = StatusExecucao.ARQUIVOS_ANEXADOS
        execucao.hashes_arquivos = json.dumps({"despesas": f_desp, "razao": f_raz, "extrato": f_ext})
        uow.commit()
    return {"message": "Files uploaded successfully", "exec_id": exec_id}

@router.post("/{exec_id}/run", status_code=202)
def run_pipeline(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403)
        
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404)
        if current_user.role != Role.ADMIN and execucao.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado a dados de outra empresa.")
        if execucao.status != StatusExecucao.ARQUIVOS_ANEXADOS: raise HTTPException(status_code=400)
        
        execucao.status = StatusExecucao.PROCESSANDO
        uow.commit()
        
        # Despacha para o Celery de forma assíncrona e resiliente
        runner = CeleryRunner()
        runner.run(exec_id)
        return {"message": "Pipeline iniciada em background pelo Celery", "exec_id": exec_id, "status": "PROCESSING"}

@router.post("/{exec_id}/approve-staging", status_code=202)
def approve_staging(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """
    Aprova os dados do Staging e inicia a Fase 2 (Conciliação).
    """
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403)
        
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404)
        if current_user.role != Role.ADMIN and execucao.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado a dados de outra empresa.")
        
        if execucao.status != StatusExecucao.AGUARDANDO_REVISAO_STAGING:
            raise HTTPException(status_code=400, detail="Execução não está aguardando revisão do staging.")
            
        execucao.status = StatusExecucao.CONCILIANDO
        uow.commit()
        
        # Despacha para o Celery para a Fase 2
        runner = CeleryRunner()
        runner.run(exec_id)
        
    return {"message": "Conciliação (Fase 2) iniciada com sucesso.", "exec_id": exec_id}

@router.get("/{exec_id}/summary")
def execution_summary(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404)
        if current_user.role != Role.ADMIN and execucao.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
            
    from app.contexts.matching_auditing.queries.get_execution_summary import GetExecutionSummaryQueryHandler
    summary = GetExecutionSummaryQueryHandler.execute(db, exec_id)
    return summary
