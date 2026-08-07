import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api import schemas
from app.contexts.identity.auth_utils import get_current_user
from app.api.deps import get_db
from app.models.domain import Usuario, Role, MatchCandidate, MovimentacaoBancaria, ParcelaDespesa, LancamentoContabil, StatusCandidato, StatusConciliacao
from app.core.uow import SQLAlchemyUnitOfWork
from app.contexts.matching_auditing.engine.core import SuggestionEngine, load_matching_profile

router = APIRouter(prefix="/executions", tags=["matching"])

@router.get("/{exec_id}/candidates")
def execution_candidates(exec_id: str, status: str = "PENDENTE_REVISAO", db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        candidatos = uow.executions.get_candidates(uow.session, exec_id, status)
        
        mov_ids = [c.movimentacao_id for c in candidatos if c.movimentacao_id]
        par_ids = [c.parcela_id for c in candidatos if c.parcela_id]
        lanc_ids = [c.lancamento_id for c in candidatos if c.lancamento_id]
        
        movs = uow.session.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.id.in_(mov_ids)).all() if mov_ids else []
        pars = uow.session.query(ParcelaDespesa).options(joinedload(ParcelaDespesa.fornecedor)).filter(ParcelaDespesa.id.in_(par_ids)).all() if par_ids else []
        lancs = uow.session.query(LancamentoContabil).filter(LancamentoContabil.id.in_(lanc_ids)).all() if lanc_ids else []
        
        mov_map = {m.id: m for m in movs}
        par_map = {p.id: p for p in pars}
        lanc_map = {l.id: l for l in lancs}
        
        results = []
        for c in candidatos:
            c_dict = c.__dict__.copy()
            if '_sa_instance_state' in c_dict: del c_dict['_sa_instance_state']
            c_dict['regras'] = json.loads(c.explanation_snapshot) if getattr(c, 'explanation_snapshot', None) else []
            
            mov = mov_map.get(c.movimentacao_id)
            par = par_map.get(c.parcela_id)
            lanc = lanc_map.get(c.lancamento_id)
            
            c_dict['movimentacao_original'] = {"historico": mov.historico if mov else "", "valor": str(mov.valor) if mov else "0.0", "data": mov.data.isoformat() if mov and mov.data else None} if mov else None
            c_dict['parcela_original'] = {"documento": par.documento_relacionado if par else "", "fornecedor": par.fornecedor.nome_normalizado if par and par.fornecedor else "", "valor": str(par.valor) if par else "0.0", "data_vencimento": par.data_vencimento.isoformat() if par and par.data_vencimento else None} if par else None
            c_dict['lancamento_original'] = {"historico": lanc.historico if lanc else "", "chave": lanc.chave if lanc else "", "debito": str(lanc.valor_debito) if lanc else "0.0", "credito": str(lanc.valor_credito) if lanc else "0.0"} if lanc else None
            results.append(c_dict)
        return results

@router.get("/{exec_id}/conciliations")
def execution_conciliations(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        itens = uow.executions.get_conciliations(uow.session, exec_id)
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
                "movimentacao": {"historico": mov.historico if mov else "", "valor": str(mov.valor) if mov else "0.0", "data": mov.data.isoformat() if mov and mov.data else None} if mov else None,
                "parcela": {"documento": par.documento_relacionado if par else "", "fornecedor": par.fornecedor.nome_normalizado if par and par.fornecedor else "", "valor": str(par.valor) if par else "0.0"} if par else None,
                "lancamento": {"historico": lanc.historico if lanc else "", "chave": lanc.chave if lanc else "", "debito": str(lanc.valor_debito) if lanc else "0.0", "credito": str(lanc.valor_credito) if lanc else "0.0"} if lanc else None
            })
        return results

@router.get("/{exec_id}/divergencies")
def execution_divergencies(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        movs = uow.executions.get_divergencies(uow.session, exec_id)
        results = []
        for m in movs:
            results.append({"mov_id": m.id, "historico": m.historico, "valor": m.valor, "data_ocorrencia": m.data, "motivo": "Nenhum candidato atingiu score."})
        return results

@router.get("/{exec_id}/logs")
def execution_logs(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    from app.models.domain import CandidateEvaluationLog
    with SQLAlchemyUnitOfWork(db) as uow:
        cands = uow.executions.get_candidates(uow.session, exec_id, "PENDENTE_REVISAO")
        cands.extend(uow.executions.get_candidates(uow.session, exec_id, "APROVADO"))
        cands.extend(uow.executions.get_candidates(uow.session, exec_id, "REJEITADO_PELO_MOTOR"))
        
        logs = uow.session.query(CandidateEvaluationLog).filter(CandidateEvaluationLog.execucao_id == exec_id).all()
        
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

# Generic matching endpoints (deprecated globally, moved to matching slice but keeping route for compatibility)
@router.post("/candidates/{id}/decision")
def review_candidate(id: str, decision: schemas.DecisionRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.role == Role.AUDITOR: raise HTTPException(status_code=403)
    
    with SQLAlchemyUnitOfWork(db) as uow:
        from sqlalchemy.exc import OperationalError
        try:
            cand = uow.session.query(MatchCandidate).filter(MatchCandidate.id == id).with_for_update(nowait=True).first()
        except OperationalError:
            raise HTTPException(status_code=409, detail="Candidato já está sendo avaliado por outro usuário (Concorrência).")
            
        if not cand: raise HTTPException(status_code=404)
        if cand.status != StatusCandidato.PENDENTE_REVISAO: raise HTTPException(status_code=400)
        
        cand.reviewed_by = current_user.id
        cand.reviewed_at = datetime.utcnow()
        cand.decision_comment = decision.comment
        
        if decision.action == "APROVAR":
            cand.status = StatusCandidato.APROVADO
            profile = load_matching_profile()
            engine = SuggestionEngine(uow.session, profile['matching_profile'], profile['version'])
            engine.persist_match(
                score=cand.score_total, 
                status=StatusConciliacao.APROVADO, 
                mov_id=str(cand.movimentacao_id), 
                parcela_id=str(cand.parcela_id) if cand.parcela_id else None, 
                lanc_id=str(cand.lancamento_id) if cand.lancamento_id else None, 
                regras_json=json.loads(cand.explanation_snapshot) if cand.explanation_snapshot else []
            )
        elif decision.action == "REJEITAR":
            cand.status = StatusCandidato.REJEITADO_PELO_MOTOR 
        else:
            raise HTTPException(status_code=400)
        uow.commit()
    return {"message": "Decisão registrada com sucesso"}
