import uuid
import yaml
import time
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain import (
    Conciliacao, ConciliacaoItem, ConciliacaoExplicacao,
    StatusConciliacao, TipoMatch,
    ExecucaoPipeline, StatusExecucao,
    MatchCandidate, StatusCandidato, CandidateEvaluationLog
)
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro, StatusTitulo
from app.models.ledger import LancamentoCabecalho, StatusLancamento
from app.contexts.matching_auditing.engine.rules import IMatchingRule, RuleResult

def load_matching_profile():
    base_dir = Path(__file__).parent.parent.parent.parent
    path = base_dir / "config" / "matching_profile.yaml"
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class CandidateGenerator:
    """Filtra candidatos"""
    def __init__(self, db_session: Session):
        self.db = db_session
        self.metrics = {
            "avaliados_total": 0,
            "descartados_data": 0,
            "descartados_valor": 0,
            "aprovados_filtro": 0
        }
        self.discard_log = []

    def get_candidates_for_movimentacao(
        self, 
        mov: MovimentacaoFinanceira, 
        titulos_pendentes: List[TituloFinanceiro],
        lancamentos_pendentes: List[LancamentoCabecalho]
    ) -> List[Tuple[Optional[TituloFinanceiro], Optional[LancamentoCabecalho], Optional[str]]]:
        
        candidatos_titulos = []
        for t in titulos_pendentes:
            self.metrics["avaliados_total"] += 1
            if not t.data_vencimento or not mov.data_transacao:
                if len(self.discard_log) < 500:
                    self.discard_log.append({"mov_id": str(mov.id), "titulo_id": str(t.id), "motivo": "Data ausente"})
                self.metrics["descartados_data"] += 1
                continue
            days_diff = abs((t.data_vencimento - mov.data_transacao).days)
            if days_diff > 10:
                if len(self.discard_log) < 500:
                    self.discard_log.append({"mov_id": str(mov.id), "titulo_id": str(t.id), "motivo": f"Data fora da janela (+-10 dias). Diff: {days_diff}"})
                self.metrics["descartados_data"] += 1
                continue
            candidatos_titulos.append(t)
            self.metrics["aprovados_filtro"] += 1

        candidatos_lancamentos = []
        for l in lancamentos_pendentes:
            if not l.data_competencia or not mov.data_transacao:
                continue
            days_diff = abs((l.data_competencia - mov.data_transacao).days)
            if days_diff > 10:
                continue
            candidatos_lancamentos.append(l)

        # Se não encontrou nem titulo nem lancamento, descarte total
        if not candidatos_titulos and not candidatos_lancamentos:
            return [(None, None, "Sem candidatos (titulo ou lançamento) no raio de 10 dias.")]

        # Combinar: se tiver de ambos, cruzamos. Mas para evitar cartesiano enorme, limitamos a 10*10 = 100.
        # Geralmente há 1-2 titulos e 1-2 lancamentos pra mesma data.
        candidatos_finais = []
        
        if candidatos_titulos and candidatos_lancamentos:
            for t in candidatos_titulos:
                for l in candidatos_lancamentos:
                    candidatos_finais.append((t, l, None))
        elif candidatos_titulos:
            for t in candidatos_titulos:
                candidatos_finais.append((t, None, None))
        elif candidatos_lancamentos:
            for l in candidatos_lancamentos:
                candidatos_finais.append((None, l, None))
                
        return candidatos_finais

class ScoringEngine:
    def __init__(self, rules: List[IMatchingRule]):
        self.rules = rules
        self.rule_stats = {r.name: {"executada": 0, "aprovou": 0, "rejeitou": 0, "peso": r.weight, "tempo_total_ms": 0.0, "score_total": 0.0} for r in rules}

    def score(self, titulo: Optional[TituloFinanceiro], mov: MovimentacaoFinanceira, lanc: Optional[LancamentoCabecalho]) -> Tuple[float, List[RuleResult], List[IMatchingRule]]:
        total_score = 0.0
        total_weight = 0.0
        details = []
        applied_rules = []
        
        for rule in self.rules:
            self.rule_stats[rule.name]["executada"] += 1
            start_t = time.perf_counter()
            result = rule.evaluate(titulo, mov, lanc)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            
            self.rule_stats[rule.name]["tempo_total_ms"] += elapsed_ms
            
            if result.confidence > 0:
                self.rule_stats[rule.name]["score_total"] += result.score
                if result.score > 50:
                    self.rule_stats[rule.name]["aprovou"] += 1
                else:
                    self.rule_stats[rule.name]["rejeitou"] += 1
                    
                total_score += (result.score * result.weight * result.confidence)
                total_weight += (result.weight * result.confidence)
                details.append(result)
                applied_rules.append(rule)
            else:
                self.rule_stats[rule.name]["rejeitou"] += 1
                
        if total_weight == 0:
            return 0.0, [], []
            
        final_score = total_score / total_weight
        return final_score, details, applied_rules

class DecisionEngine:
    def __init__(self, threshold_auto: float, threshold_review: float):
        self.t_auto = threshold_auto
        self.t_review = threshold_review

    def decide(self, score: float) -> Optional[StatusConciliacao]:
        if score >= self.t_auto:
            return StatusConciliacao.APROVADO
        elif score >= self.t_review:
            return StatusConciliacao.PENDENTE
        return None

class SuggestionEngine:
    def __init__(self, db_session: Session, profile_name: str, profile_version: str):
        self.db = db_session
        self.profile_name = profile_name
        self.profile_version = profile_version

    def _to_uuid(self, val):
        if val is None: return None
        if isinstance(val, uuid.UUID): return val
        return uuid.UUID(str(val))

    def persist_match(
        self, score: float, 
        status: StatusConciliacao, 
        mov_id: Any, 
        titulo_id: Optional[Any], 
        lanc_id: Optional[Any],
        regras_json: List[dict]
    ) -> Conciliacao:
        conciliacao = Conciliacao(
            id=str(uuid.uuid4()),
            status=status,
            tipo_match=TipoMatch.UM_PARA_UM,
            score_match=int(score),
            regra_utilizada="StrategyBasedEngine",
            matching_profile=self.profile_name,
            explainability_version=self.profile_version
        )
        self.db.add(conciliacao)
        
        item = ConciliacaoItem(
            id=str(uuid.uuid4()),
            conciliacao_id=conciliacao.id,
            titulo_id=str(titulo_id) if titulo_id else None,
            movimentacao_financeira_id=str(mov_id) if mov_id else None,
            lancamento_cabecalho_id=self._to_uuid(lanc_id)
        )
        self.db.add(item)

        # Atualizar entidades financeiras e registrar ConciliacaoFinanceira
        mov = self.db.query(MovimentacaoFinanceira).filter(MovimentacaoFinanceira.id == str(mov_id)).first()
        if mov:
            mov.conciliada = True

            if titulo_id:
                titulo = self.db.query(TituloFinanceiro).filter(TituloFinanceiro.id == str(titulo_id)).first()
                if titulo:
                    from app.models.financeiro import ConciliacaoFinanceira, StatusTitulo
                    titulo.status = StatusTitulo.LIQUIDADO
                    titulo.valor_pago = abs(mov.valor)
                    titulo.data_pagamento = mov.data_transacao

                    cf = ConciliacaoFinanceira(
                        id=str(uuid.uuid4()),
                        empresa_id=mov.empresa_id,
                        titulo_id=titulo.id,
                        movimentacao_id=mov.id,
                        valor_conciliado=abs(mov.valor),
                        data_conciliacao=mov.data_transacao,
                        match_automatico=True,
                        confianca_match=float(score) / 100.0
                    )
                    self.db.add(cf)
        
        for rule in regras_json:
            explicacao = ConciliacaoExplicacao(
                id=str(uuid.uuid4()),
                conciliacao_id=conciliacao.id,
                regra=rule['nome'],
                score=rule['score'],
                peso=rule['peso'],
                confidence=rule.get('confidence', 1.0),
                justificativa=rule['justificativa'],
                matching_profile=self.profile_name,
                explainability_version=self.profile_version
            )
            self.db.add(explicacao)
            
        return conciliacao

class MatchOrchestrator:
    def __init__(self, db_session: Session, execucao_id: str = None):
        self.db = db_session
        self.profile = load_matching_profile()
        self.candidate_gen = CandidateGenerator(db_session)
        
        # Recuperar ou criar a execução
        if execucao_id:
            self.execucao = self.db.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
        else:
            self.execucao = ExecucaoPipeline(id=str(uuid.uuid4()), matching_profile=self.profile['matching_profile'], runtime_profile="production")
            self.db.add(self.execucao)
            
        self.execucao.status = StatusExecucao.PROCESSANDO
        self.execucao.data_inicio = datetime.utcnow()
        self.db.commit()
        
        weights = self.profile['weights']
        thresholds = self.profile['thresholds']
        
        from app.contexts.matching_auditing.engine.rules import ValueRule, DateRule, PixRule
        self.scoring = ScoringEngine([
            ValueRule(weight=weights.get('ValueRule', 2.0)),
            DateRule(weight=weights.get('DateRule', 1.5)),
            PixRule(weight=weights.get('PixRule', 3.0))
        ])
        
        self.decision = DecisionEngine(threshold_auto=thresholds['auto'], threshold_review=thresholds['review'])
        self.suggestion = SuggestionEngine(db_session, self.profile['matching_profile'], self.profile['version'])
        
        self.reconciliation_log = []
        self.divergencias_log = []
        self.candidates_discard_engine_log = []
        
        self.start_time = time.perf_counter()

    def run_pipeline(self) -> Dict[str, Any]:
        empresa_id = self.execucao.empresa_id if self.execucao else None

        movs_q = self.db.query(MovimentacaoFinanceira).filter(MovimentacaoFinanceira.conciliada == False)
        titulos_q = self.db.query(TituloFinanceiro).filter(TituloFinanceiro.status.in_(['ABERTO', StatusTitulo.ABERTO]))
        lanc_q = self.db.query(LancamentoCabecalho).filter(LancamentoCabecalho.status.in_(['RASCUNHO', StatusLancamento.RASCUNHO]))

        if empresa_id:
            movs_q = movs_q.filter(MovimentacaoFinanceira.empresa_id == empresa_id)
            titulos_q = titulos_q.filter(TituloFinanceiro.empresa_id == empresa_id)
            lanc_q = lanc_q.filter(LancamentoCabecalho.empresa_id == empresa_id)

        movs = movs_q.all()
        titulos = titulos_q.all()
        lancamentos = lanc_q.all()
        
        conciliados_mov = self.db.query(ConciliacaoItem.movimentacao_financeira_id).all()
        conciliados_mov_ids = {c[0] for c in conciliados_mov if c[0]}
        
        movs_pendentes = [m for m in movs if m.id not in conciliados_mov_ids]
        
        stats = {
            "total_movimentos": len(movs),
            "candidatos_avaliados": 0,
            "matches_automaticos": 0,
            "matches_revisao": 0,
            "divergencias": 0,
            "profile_version": self.profile['version'],
            "profile_name": self.profile['matching_profile']
        }
        
        for mov in movs_pendentes:
            candidatos_avaliados = self.candidate_gen.get_candidates_for_movimentacao(mov, titulos, lancamentos)
            stats["candidatos_avaliados"] += len([c for c in candidatos_avaliados if c[2] is None])
            
            best_score = 0.0
            best_candidate = None
            best_details = []
            best_rules = []
            
            # Persistir descartes do generator no funil leve (máximo 500 para performance)
            eval_log_count = 0
            for t, l, motivo in candidatos_avaliados:
                if motivo and eval_log_count < 500:
                    cel = CandidateEvaluationLog(
                        id=str(uuid.uuid4()), execucao_id=self.execucao.id, movimentacao_financeira_id=mov.id, 
                        titulo_id=t.id if t else None, lancamento_cabecalho_id=l.id if l else None,
                        motivo_descarte=motivo
                    )
                    self.db.add(cel)
                    eval_log_count += 1
            
            # Avaliar válidos
            valid_candidates = [c for c in candidatos_avaliados if c[2] is None]
            candidatos_analisados = []
            
            for t, l, _ in valid_candidates:
                score, details, applied = self.scoring.score(t, mov, l)
                regras_json = [{"nome": r.name, "score": d.score, "peso": d.weight, "confidence": d.confidence, "justificativa": d.reason} for r, d in zip(applied, details)]
                candidatos_analisados.append({
                    "t": t, "l": l,
                    "score": score,
                    "regras_json": regras_json
                })
                
                if score > best_score:
                    best_score = score
                    best_candidate = (t, l)
                    best_details = details
                    best_rules = applied

            # Persistir os candidatos analisados pelo Scoring Engine
            for c in candidatos_analisados:
                t, l = c["t"], c["l"]
                score = c["score"]
                regras_json = c["regras_json"]
                
                if (t, l) == best_candidate and best_score > 0:
                    status = self.decision.decide(best_score)
                    
                    if status == StatusConciliacao.APROVADO:
                        # Auto match!
                        mc_status = StatusCandidato.APROVADO
                        stats["matches_automaticos"] += 1
                        
                        # Criar conciliação oficial direto
                        self.suggestion.persist_match(score, status, str(mov.id), str(t.id) if t else None, str(l.id) if l else None, regras_json)
                        if t in titulos: titulos.remove(t)
                    elif status == StatusConciliacao.PENDENTE:
                        # Human review needed
                        mc_status = StatusCandidato.PENDENTE_REVISAO
                        stats["matches_revisao"] += 1
                        if t in titulos: titulos.remove(t)
                    else:
                        mc_status = StatusCandidato.REJEITADO_PELO_MOTOR
                        motivo_descarte = f"Melhor score ({score:.2f}) não atingiu o threshold."
                else:
                    # Perdeu pra outro ou score zero
                    mc_status = StatusCandidato.REJEITADO_PELO_MOTOR
                    motivo_descarte = f"Score insuficiente ou menor que o vencedor ({best_score:.2f})"
                    self.candidates_discard_engine_log.append({
                        "mov_id": str(mov.id), "titulo_id": str(t.id) if t else None, 
                        "motivo": motivo_descarte, "score": score
                    })

                mc = MatchCandidate(
                    id=str(uuid.uuid4()), execucao_id=self.execucao.id, movimentacao_financeira_id=mov.id, titulo_id=t.id if t else None, lancamento_cabecalho_id=l.id if l else None,
                    score_total=score, status=mc_status, motivo_descarte=motivo_descarte if mc_status == StatusCandidato.REJEITADO_PELO_MOTOR else None,
                    explanation_snapshot=json.dumps(regras_json)
                )
                self.db.add(mc)

                # Mantendo LOGs compatíveis para E2E CSV
                if mc_status in (StatusCandidato.APROVADO, StatusCandidato.PENDENTE_REVISAO):
                    self.reconciliation_log.append({
                        "mov_id": str(mov.id), "mov_desc": mov.descricao_extrato, "mov_valor": float(mov.valor),
                        "titulo_id": str(t.id) if t else None, "lancamento_id": str(l.id) if l else None,
                        "score": score, "status": "APROVADO" if mc_status == StatusCandidato.APROVADO else "PENDENTE",
                        "regras": regras_json
                    })

            if not best_candidate or self.decision.decide(best_score) is None:
                stats["divergencias"] += 1
                self.divergencias_log.append({"mov_id": str(mov.id), "historico": mov.descricao_extrato, "valor": float(mov.valor), "motivo": "Sem match final"})
                
        # Finalizar Execução
        self.execucao.status = StatusExecucao.CONCLUIDA
        self.execucao.data_fim = datetime.utcnow()
        self.execucao.duracao_ms = (time.perf_counter() - self.start_time) * 1000.0
        
        self.db.commit()
        return stats
