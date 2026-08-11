import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from app.api import schemas
from app.contexts.identity.auth_utils import get_current_user
from app.api.deps import get_db
from app.models.domain import Usuario, Role, MatchCandidate, StatusCandidato, StatusConciliacao, ExecucaoPipeline
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro
from app.models.ledger import LancamentoCabecalho
from app.core.uow import SQLAlchemyUnitOfWork
from app.contexts.matching_auditing.engine.core import SuggestionEngine, load_matching_profile

router = APIRouter(prefix="/executions", tags=["matching"])

def _enforce_tenant_access(uow: SQLAlchemyUnitOfWork, exec_id: str, current_user: Usuario):
    execucao = uow.session.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    if not execucao:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    if current_user.role != Role.ADMIN and execucao.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta execução (Tenant Isolation).")
    return execucao

@router.get("/{exec_id}/candidates")
def execution_candidates(exec_id: str, status: str = "PENDENTE_REVISAO", db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        _enforce_tenant_access(uow, exec_id, current_user)
        candidatos = uow.executions.get_candidates(uow.session, exec_id, status)
        
        mov_ids = [c.movimentacao_financeira_id for c in candidatos if c.movimentacao_financeira_id]
        titulo_ids = [c.titulo_id for c in candidatos if c.titulo_id]
        lanc_ids = [c.lancamento_cabecalho_id for c in candidatos if c.lancamento_cabecalho_id]
        
        movs = uow.session.query(MovimentacaoFinanceira).filter(MovimentacaoFinanceira.id.in_(mov_ids)).all() if mov_ids else []
        titulos = uow.session.query(TituloFinanceiro).filter(TituloFinanceiro.id.in_(titulo_ids)).all() if titulo_ids else []
        lancs = uow.session.query(LancamentoCabecalho).options(joinedload(LancamentoCabecalho.partidas)).filter(LancamentoCabecalho.id.in_(lanc_ids)).all() if lanc_ids else []
        
        mov_map = {str(m.id): m for m in movs}
        titulo_map = {str(t.id): t for t in titulos}
        lanc_map = {str(l.id): l for l in lancs}
        
        results = []
        for c in candidatos:
            c_dict = c.__dict__.copy()
            if '_sa_instance_state' in c_dict: del c_dict['_sa_instance_state']
            c_dict['regras'] = json.loads(c.explanation_snapshot) if getattr(c, 'explanation_snapshot', None) else []
            
            mov = mov_map.get(str(c.movimentacao_financeira_id))
            titulo = titulo_map.get(str(c.titulo_id))
            lanc = lanc_map.get(str(c.lancamento_cabecalho_id))
            
            c_dict['transacao_original'] = {
                "historico": mov.descricao_extrato if mov else "",
                "valor": str(mov.valor) if mov else "0.0",
                "data": mov.data_transacao.isoformat() if mov and mov.data_transacao else None
            } if mov else None
            c_dict['titulo_original'] = {
                "descricao": titulo.descricao if titulo else "",
                "fornecedor": titulo.fornecedor_cliente_nome if titulo else "",
                "valor": str(titulo.valor_nominal) if titulo else "0.0",
                "data_vencimento": titulo.data_vencimento.isoformat() if titulo and titulo.data_vencimento else None
            } if titulo else None
            c_dict['lancamento_original'] = {
                "historico": lanc.historico_padrao if lanc else "",
                "numero_lote": lanc.numero_lote if lanc else "",
                "total_partidas": len(lanc.partidas) if lanc else 0
            } if lanc else None
            results.append(c_dict)
        return results

@router.get("/{exec_id}/conciliations")
def execution_conciliations(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        _enforce_tenant_access(uow, exec_id, current_user)
        itens = uow.executions.get_conciliations(uow.session, exec_id)
        results = []
        for item in itens:
            c = item.conciliacao
            mov = item.movimentacao_financeira
            titulo = item.titulo
            lanc = item.lancamento
            results.append({
                "conciliacao_id": c.id,
                "status": c.status.name,
                "aprovado_por": c.aprovado_por,
                "data_conciliacao": c.data_criacao.isoformat() if c.data_criacao else None,
                "score": c.score_match,
                "transacao": {
                    "historico": mov.descricao_extrato if mov else "",
                    "valor": str(mov.valor) if mov else "0.0",
                    "data": mov.data_transacao.isoformat() if mov and mov.data_transacao else None
                } if mov else None,
                "titulo": {
                    "descricao": titulo.descricao if titulo else "",
                    "fornecedor": titulo.fornecedor_cliente_nome if titulo else "",
                    "valor": str(titulo.valor_nominal) if titulo else "0.0"
                } if titulo else None,
                "lancamento": {
                    "historico": lanc.historico_padrao if lanc else "",
                    "numero_lote": lanc.numero_lote if lanc else ""
                } if lanc else None
            })
        return results

@router.get("/{exec_id}/divergencies")
def execution_divergencies(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        _enforce_tenant_access(uow, exec_id, current_user)
        movs = uow.executions.get_divergencies(uow.session, exec_id)
        results = []
        for m in movs:
            results.append({"mov_id": m.id, "historico": m.descricao_extrato, "valor": m.valor, "data_ocorrencia": m.data_transacao, "motivo": "Nenhum candidato atingiu score."})
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

@router.get("/{exec_id}/export")
def export_accounting_entries(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        _enforce_tenant_access(uow, exec_id, current_user)
        lancamentos = uow.session.query(LancamentoCabecalho).filter(
            LancamentoCabecalho.empresa_id == current_user.empresa_id
        ).options(joinedload(LancamentoCabecalho.partidas)).all()
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Cabeçalho padrão
        writer.writerow(["DATA", "CONTA_DEBITO", "CONTA_CREDITO", "VALOR", "HISTORICO", "LOTE"])
        
        for lanc in lancamentos:
            for partida in lanc.partidas:
                conta_deb = str(partida.conta_contabil_id) if partida.natureza.value == "D" else ""
                conta_cred = str(partida.conta_contabil_id) if partida.natureza.value == "C" else ""
                writer.writerow([
                    lanc.data_competencia.strftime("%d/%m/%Y") if lanc.data_competencia else "",
                    conta_deb,
                    conta_cred,
                    f"{partida.valor:.2f}".replace('.', ','),
                    lanc.historico_padrao,
                    lanc.numero_lote
                ])
            
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=lancamentos_{exec_id[:8]}.csv"}
        )

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
        _enforce_tenant_access(uow, cand.execucao_id, current_user)
        
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
                mov_id=str(cand.movimentacao_financeira_id), 
                titulo_id=str(cand.titulo_id) if cand.titulo_id else None, 
                lanc_id=str(cand.lancamento_cabecalho_id) if cand.lancamento_cabecalho_id else None, 
                regras_json=json.loads(cand.explanation_snapshot) if cand.explanation_snapshot else []
            )
        elif decision.action == "REJEITAR":
            cand.status = StatusCandidato.REJEITADO_PELO_MOTOR 
        else:
            raise HTTPException(status_code=400)
        uow.commit()
        
        from app.core.events import EventBus
        EventBus.publish("MatchDecisionEvent", cand_id=id, action=decision.action)

    return {"message": "Decisão processada", "status": cand.status.name}
