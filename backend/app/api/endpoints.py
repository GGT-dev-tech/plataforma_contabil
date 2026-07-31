from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
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

@router.get("/auth/seed-admin")
def run_seed_admin_get():
    import traceback
    from app.scripts_runner import run_startup_tasks
    try:
        run_startup_tasks()
        return {"message": "Startup tasks executed successfully!"}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@router.post("/auth/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    if db.query(Usuario).first():
        raise HTTPException(status_code=400, detail="Banco já populado")
    admin = Usuario(id=str(uuid.uuid4()), email="admin@contabil.com", hashed_password=get_password_hash("admin123"), nome="Administrador", role=Role.ADMIN)
    analista = Usuario(id=str(uuid.uuid4()), email="analista@contabil.com", hashed_password=get_password_hash("analista123"), nome="Analista", role=Role.ANALISTA)
    auditor = Usuario(id=str(uuid.uuid4()), email="auditor@contabil.com", hashed_password=get_password_hash("auditor123"), nome="Auditor", role=Role.AUDITOR)
    db.add_all([admin, analista, auditor])
    db.commit()
    return {"message": "Usuários criados"}


# ----------------- EXECUÇÕES (EXECUTION-CENTRIC) -----------------
@router.get("/executions")
def list_executions(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import ExecucaoPipeline
    execs = db.query(ExecucaoPipeline).order_by(ExecucaoPipeline.data_inicio.desc()).all()
    return [{
        "id": e.id,
        "status": e.status.name,
        "data_inicio": e.data_inicio,
        "data_fim": e.data_fim
    } for e in execs]

@router.get("/executions/{exec_id}")
def get_execution(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import ExecucaoPipeline
    e = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not e: raise HTTPException(status_code=404, detail="Não encontrado")
    return {
        "id": e.id,
        "status": e.status.name,
        "data_inicio": e.data_inicio,
        "data_fim": e.data_fim,
        "matching_profile": e.matching_profile
    }

@router.post("/executions", response_model=schemas.ExecucaoPipelineSchema)
def create_execution(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import ExecucaoPipeline, StatusExecucao
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403, detail="Permissão negada")
    execucao = ExecucaoPipeline(id=str(uuid.uuid4()), status=StatusExecucao.CRIADA, matching_profile="financeiro_2026", runtime_profile="api")
    db.add(execucao)
    db.commit()
    db.refresh(execucao)
    return execucao

@router.post("/executions/{exec_id}/files", status_code=202)
def upload_files(exec_id: str, despesas: UploadFile = File(...), razao: UploadFile = File(...), extrato: UploadFile = File(...), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import ExecucaoPipeline, StatusExecucao, ImportacaoArquivo, TipoArquivo
    from app.services.storage import LocalStorageProvider
    import hashlib
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not execucao: raise HTTPException(status_code=404)
    storage = LocalStorageProvider()
    
    def save_and_hash(file_upload, tipo):
        content = file_upload.file.read()
        file_upload.file.seek(0)
        sha256 = hashlib.sha256(content).hexdigest()
        tamanho = len(content)
        path = storage.save(exec_id, file_upload.filename, file_upload.file)
        arquivo = ImportacaoArquivo(id=str(uuid.uuid4()), execucao_id=exec_id, nome_original=file_upload.filename, tipo=tipo, storage_path=path, hash_sha256=sha256, tamanho_bytes=tamanho, uploaded_by=current_user.id)
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
def run_pipeline(exec_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import ExecucaoPipeline, StatusExecucao
    from app.pipeline.runner import SyncRunner
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403)
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not execucao: raise HTTPException(status_code=404)
    if execucao.status != StatusExecucao.ARQUIVOS_ANEXADOS: raise HTTPException(status_code=400)
    execucao.status = StatusExecucao.PROCESSANDO
    db.commit()
    runner = SyncRunner(background_tasks, db)
    runner.run(exec_id)
    return {"message": "Pipeline iniciada em background", "exec_id": exec_id, "status": "PROCESSING"}

@router.get("/executions/{exec_id}/summary")
def execution_summary(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MovimentacaoBancaria, MatchCandidate, ConciliacaoItem, Conciliacao
    movs_count = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.execucao_id == exec_id).count()
    # Aprovados count based on candidates or Conciliacoes? We use Conciliacoes that match movs from this execution
    # Wait, Conciliacao doesn't have execucao_id. But MatchCandidate has.
    approved_count = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == exec_id, MatchCandidate.status == 'APROVADO').count()
    pending_count = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == exec_id, MatchCandidate.status == 'PENDENTE_REVISAO').count()
    rejected_count = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == exec_id, MatchCandidate.status == 'REJEITADO_PELO_MOTOR').count()
    return {
        "total_movimentacoes": movs_count,
        "total_aprovados": approved_count,
        "total_pendentes": pending_count,
        "total_rejeitados": rejected_count
    }

@router.get("/executions/{exec_id}/candidates")
def execution_candidates(exec_id: str, status: str = "PENDENTE_REVISAO", db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MatchCandidate, MovimentacaoBancaria, ParcelaDespesa
    candidatos = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == exec_id, MatchCandidate.status == status).all()
    results = []
    for c in candidatos:
        c_dict = c.__dict__.copy()
        if '_sa_instance_state' in c_dict: del c_dict['_sa_instance_state']
        c_dict['regras'] = json.loads(c.explanation_snapshot) if c.explanation_snapshot else []
        from app.models.domain import LancamentoContabil
        mov = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.id == c.movimentacao_id).first()
        par = db.query(ParcelaDespesa).filter(ParcelaDespesa.id == c.parcela_id).first() if getattr(c, 'parcela_id', None) else None
        lanc = db.query(LancamentoContabil).filter(LancamentoContabil.id == c.lancamento_id).first() if getattr(c, 'lancamento_id', None) else None
        
        c_dict['movimentacao_original'] = {"historico": mov.historico if mov else "", "valor": str(mov.valor) if mov else "0.0", "data": mov.data.isoformat() if mov and mov.data else None}
        c_dict['parcela_original'] = {"documento": par.documento_relacionado if par else "", "fornecedor": par.fornecedor.nome_normalizado if par and par.fornecedor else "", "valor": str(par.valor) if par else "0.0", "data_vencimento": par.data_vencimento.isoformat() if par and par.data_vencimento else None} if par else None
        c_dict['lancamento_original'] = {"historico": lanc.historico if lanc else "", "chave": lanc.chave if lanc else "", "debito": str(lanc.valor_debito) if lanc else "0.0", "credito": str(lanc.valor_credito) if lanc else "0.0"} if lanc else None
        results.append(c_dict)
    return results

@router.get("/executions/{exec_id}/conciliations")
def execution_conciliations(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MatchCandidate, ConciliacaoItem, Conciliacao, MovimentacaoBancaria, ParcelaDespesa
    # We find Conciliacao items by finding MatchCandidates that are approved for this execucao,
    # then resolving their mov/parcela. Wait, Conciliacao doesn't store execucao_id.
    # The true way is to get Movimentacoes of this execucao, then their Conciliacoes.
    movs = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.execucao_id == exec_id).all()
    mov_ids = [m.id for m in movs]
    itens = db.query(ConciliacaoItem).filter(ConciliacaoItem.movimentacao_id.in_(mov_ids)).all()
    results = []
    for item in itens:
        c = item.conciliacao
        mov = item.movimentacao
        par = item.parcela
        lanc = item.lancamento
        results.append({
            "conciliacao_id": c.id,
            "status": c.status.name,
            "aprovado_por": c.aprovado_por,
            "data_conciliacao": c.data_criacao.isoformat() if c.data_criacao else None,
            "score": c.score_match,
            "movimentacao": {"historico": mov.historico if mov else "", "valor": str(mov.valor) if mov else "0.0", "data": mov.data.isoformat() if mov and mov.data else None},
            "parcela": {"documento": par.documento_relacionado if par else "", "fornecedor": par.fornecedor.nome_normalizado if par and par.fornecedor else "", "valor": str(par.valor) if par else "0.0"} if par else None,
            "lancamento": {"historico": lanc.historico if lanc else "", "chave": lanc.chave if lanc else "", "debito": str(lanc.valor_debito) if lanc else "0.0", "credito": str(lanc.valor_credito) if lanc else "0.0"} if lanc else None
        })
    return results

@router.get("/executions/{exec_id}/divergencies")
def execution_divergencies(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MovimentacaoBancaria, MatchCandidate
    from sqlalchemy import not_, exists
    stmt = exists().where(MatchCandidate.movimentacao_id == MovimentacaoBancaria.id).where(MatchCandidate.status.in_(["APROVADO", "PENDENTE_REVISAO"]))
    movs = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.execucao_id == exec_id, not_(stmt)).all()
    results = []
    for m in movs:
        results.append({"mov_id": m.id, "historico": m.historico, "valor": m.valor, "data_ocorrencia": m.data, "motivo": "Nenhum candidato atingiu score."})
    return results

@router.get("/executions/{exec_id}/logs")
def execution_logs(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import CandidateEvaluationLog, ExecucaoPipeline, MatchCandidate
    logs = db.query(CandidateEvaluationLog).filter(CandidateEvaluationLog.execucao_id == exec_id).all()
    cands = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == exec_id).all()
    
    events = []
    for c in cands:
        events.append({
            "type": "CANDIDATE_GENERATED",
            "timestamp": c.data_criacao.isoformat() if hasattr(c, 'data_criacao') and c.data_criacao else None,
            "status": c.status.name,
            "score": c.score_total,
            "details": f"Gerado candidato com score {c.score_total}."
        })
    for l in logs:
        events.append({
            "type": "CANDIDATE_REJECTED",
            "timestamp": l.data_avaliacao.isoformat() if hasattr(l, 'data_avaliacao') and l.data_avaliacao else None,
            "status": "REJEITADO_PELO_GERADOR",
            "score": 0,
            "details": f"Descartado: {l.motivo_descarte}"
        })
    return sorted(events, key=lambda x: x.get('timestamp') or "")

# ----------------- APROVAÇÃO (DEPRECATED) -----------------
@router.get("/candidates", response_model=List[Dict[str, Any]], deprecated=True)
def list_candidates_global(status: str = "PENDENTE_REVISAO", db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return [] # Deprecated, use execution-specific instead

@router.post("/candidates/{id}/decision")
def review_candidate(id: str, decision: schemas.DecisionRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import MatchCandidate, StatusCandidato, StatusConciliacao
    from app.engine.core import SuggestionEngine, load_matching_profile
    if current_user.role == Role.AUDITOR: raise HTTPException(status_code=403)
    cand = db.query(MatchCandidate).filter(MatchCandidate.id == id).first()
    if not cand: raise HTTPException(status_code=404)
    if cand.status != StatusCandidato.PENDENTE_REVISAO: raise HTTPException(status_code=400)
    cand.reviewed_by = current_user.id
    cand.reviewed_at = datetime.utcnow()
    cand.decision_comment = decision.comment
    if decision.action == "APROVAR":
        cand.status = StatusCandidato.APROVADO
        profile = load_matching_profile()
        engine = SuggestionEngine(db, profile['matching_profile'], profile['version'])
        engine.persist_match(score=cand.score_total, status=StatusConciliacao.APROVADO, mov_id=str(cand.movimentacao_id), parcela_id=str(cand.parcela_id) if cand.parcela_id else None, lanc_id=str(cand.lancamento_id) if cand.lancamento_id else None, regras_json=json.loads(cand.explanation_snapshot) if cand.explanation_snapshot else [])
    elif decision.action == "REJEITAR":
        cand.status = StatusCandidato.REJEITADO_PELO_MOTOR 
    else:
        raise HTTPException(status_code=400)
    db.commit()
    return {"message": "Decisão registrada com sucesso"}

@router.get("/divergencies", response_model=List[schemas.DivergenciaSchema], deprecated=True)
def list_divergencies_global(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return [] # Deprecated

