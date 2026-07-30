from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.api import schemas
from app.api.auth import get_current_user, create_access_token, verify_password, get_password_hash
from app.models.domain import Usuario, Role
from datetime import datetime, timedelta
import json
import uuid

from app.api.deps import get_db

router = APIRouter()

# ----------------- AUTHENTICATION -----------------
@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "nome": user.nome,
        "role": user.role.value
    })
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para criar seed admin caso banco vazio (Apenas para testes do MVP)
@router.post("/auth/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    if db.query(Usuario).first():
        raise HTTPException(status_code=400, detail="Banco já populado")
    admin = Usuario(
        id=str(uuid.uuid4()),
        email="admin@contabil.com",
        hashed_password=get_password_hash("admin123"),
        nome="Administrador",
        role=Role.ADMIN
    )
    analista = Usuario(
        id=str(uuid.uuid4()),
        email="analista@contabil.com",
        hashed_password=get_password_hash("analista123"),
        nome="Analista",
        role=Role.ANALISTA
    )
    auditor = Usuario(
        id=str(uuid.uuid4()),
        email="auditor@contabil.com",
        hashed_password=get_password_hash("auditor123"),
        nome="Auditor",
        role=Role.AUDITOR
    )
    db.add(admin)
    db.add(analista)
    db.add(auditor)
    db.commit()
    return {"message": "Usuários de teste criados (admin, analista, auditor). Senha = <role>123"}


# ----------------- EXECUÇÕES -----------------
@router.post("/executions", response_model=schemas.ExecucaoPipelineSchema)
def create_execution(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Cria uma nova Execução de Pipeline"""
    from app.models.domain import ExecucaoPipeline, StatusExecucao
    
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403, detail="Apenas analistas ou admins podem criar execuções")
        
    execucao = ExecucaoPipeline(
        id=str(uuid.uuid4()),
        status=StatusExecucao.CRIADA,
        matching_profile="financeiro_2026",
        runtime_profile="api"
    )
    db.add(execucao)
    db.commit()
    db.refresh(execucao)
    return execucao

@router.post("/executions/{exec_id}/files", status_code=202)
def upload_files(
    exec_id: str, 
    despesas: UploadFile = File(...),
    razao: UploadFile = File(...),
    extrato: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Anexa arquivos usando StorageProvider de forma imutável"""
    from app.models.domain import ExecucaoPipeline, StatusExecucao, ImportacaoArquivo, TipoArquivo
    from app.services.storage import LocalStorageProvider
    import hashlib
    
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not execucao:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
        
    storage = LocalStorageProvider()
    
    def save_and_hash(file_upload, tipo):
        # Ler para memoria, calcular hash, salvar
        content = file_upload.file.read()
        file_upload.file.seek(0)
        sha256 = hashlib.sha256(content).hexdigest()
        tamanho = len(content)
        
        path = storage.save(exec_id, file_upload.filename, file_upload.file)
        
        arquivo = ImportacaoArquivo(
            id=str(uuid.uuid4()),
            execucao_id=exec_id,
            nome_original=file_upload.filename,
            tipo=tipo,
            storage_path=path,
            hash_sha256=sha256,
            tamanho_bytes=tamanho,
            uploaded_by=current_user.id
        )
        db.add(arquivo)
        return file_upload.filename
        
    f_desp = save_and_hash(despesas, TipoArquivo.DESPESA)
    f_raz = save_and_hash(razao, TipoArquivo.RAZAO)
    f_ext = save_and_hash(extrato, TipoArquivo.EXTRATO)
    
    execucao.status = StatusExecucao.ARQUIVOS_ANEXADOS
    execucao.hashes_arquivos = json.dumps({"despesas": f_desp, "razao": f_raz, "extrato": f_ext})
    
    db.commit()
    return {"message": "Files uploaded successfully", "exec_id": exec_id}

@router.post("/executions/{exec_id}/run", status_code=202)
def run_pipeline(
    exec_id: str, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dispara a execução do MatchOrchestrator assincronamente (MVP via BackgroundTasks)"""
    from app.models.domain import ExecucaoPipeline, StatusExecucao
    from app.pipeline.runner import SyncRunner
    
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403, detail="Sem permissão para rodar pipeline")
    
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not execucao:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    if execucao.status != StatusExecucao.ARQUIVOS_ANEXADOS:
        raise HTTPException(status_code=400, detail="Arquivos não anexados ou execução já iniciada")
        
    execucao.status = StatusExecucao.PROCESSANDO
    db.commit()
    
    runner = SyncRunner(background_tasks, db)
    runner.run(exec_id)
    
    return {"message": "Pipeline iniciada em background", "exec_id": exec_id, "status": "PROCESSING"}

# ----------------- APROVAÇÃO -----------------

@router.get("/candidates", response_model=List[Dict[str, Any]])
def list_candidates(status: str = "PENDENTE_REVISAO", db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MatchCandidate, MovimentacaoBancaria, ParcelaDespesa
    candidatos = db.query(MatchCandidate).filter(MatchCandidate.status == status).all()
    
    results = []
    for c in candidatos:
        c_dict = c.__dict__.copy()
        c_dict['regras'] = json.loads(c.explanation_snapshot) if c.explanation_snapshot else []
        
        # Enriquecer com dados originais para Human-in-the-Loop
        mov = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.id == c.movimentacao_id).first()
        par = db.query(ParcelaDespesa).filter(ParcelaDespesa.id == c.parcela_id).first() if c.parcela_id else None
        
        c_dict['movimentacao_original'] = {
            "historico": mov.historico if mov else "",
            "valor": str(mov.valor) if mov else "0.0",
            "data": mov.data.isoformat() if mov and mov.data else None
        }
        
        c_dict['parcela_original'] = {
            "documento": par.documento_relacionado if par else "",
            "fornecedor": par.fornecedor.nome_normalizado if par and par.fornecedor else "",
            "valor": str(par.valor) if par else "0.0",
            "data_vencimento": par.data_vencimento.isoformat() if par and par.data_vencimento else None
        }
        
        results.append(c_dict)
        
    return results

@router.post("/candidates/{id}/decision")
def review_candidate(id: str, decision: schemas.DecisionRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Aprova ou Rejeita um MatchCandidate manualmente com Identity Rastreável"""
    from app.models.domain import MatchCandidate, StatusCandidato, StatusConciliacao
    from app.engine.core import SuggestionEngine, load_matching_profile
    
    if current_user.role == Role.AUDITOR:
        raise HTTPException(status_code=403, detail="Auditores têm acesso apenas de leitura. Não podem aprovar conciliações.")
        
    cand = db.query(MatchCandidate).filter(MatchCandidate.id == id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidato não encontrado")
        
    if cand.status != StatusCandidato.PENDENTE_REVISAO:
        raise HTTPException(status_code=400, detail="Candidato não está pendente de revisão")
        
    cand.reviewed_by = current_user.id
    cand.reviewed_at = datetime.utcnow()
    cand.decision_comment = decision.comment
    
    if decision.action == "APROVAR":
        cand.status = StatusCandidato.APROVADO
        
        # Converte em Conciliacao Oficial
        profile = load_matching_profile()
        engine = SuggestionEngine(db, profile['matching_profile'], profile['version'])
        engine.persist_match(
            score=cand.score_total,
            status=StatusConciliacao.APROVADO,
            mov_id=str(cand.movimentacao_id),
            parcela_id=str(cand.parcela_id) if cand.parcela_id else None,
            lanc_id=None,
            regras_json=json.loads(cand.explanation_snapshot) if cand.explanation_snapshot else []
        )
    elif decision.action == "REJEITAR":
        cand.status = StatusCandidato.REJEITADO_PELO_MOTOR # Ou criar REJEITADO_HUMANO no enum
    else:
        raise HTTPException(status_code=400, detail="Ação inválida")
        
    db.commit()
    return {"message": "Decisão registrada com sucesso"}

@router.get("/divergencies", response_model=List[schemas.DivergenciaSchema])
def list_divergencies(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MovimentacaoBancaria, MatchCandidate
    from sqlalchemy import not_, exists
    stmt = exists().where(MatchCandidate.movimentacao_id == MovimentacaoBancaria.id).where(
        MatchCandidate.status.in_(["APROVADO", "PENDENTE_REVISAO"])
    )
    movs = db.query(MovimentacaoBancaria).filter(not_(stmt)).all()
    
    results = []
    for m in movs:
        results.append({
            "mov_id": m.id,
            "historico": m.historico,
            "valor": m.valor,
            "data_ocorrencia": m.data,
            "motivo": "Nenhum candidato atingiu score de aprovação ou revisão."
        })
    return results
