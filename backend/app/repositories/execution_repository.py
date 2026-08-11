from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import not_, exists
from app.repositories.base import BaseRepository
from app.models.domain import ExecucaoPipeline, StagingRegistro, MatchCandidate, ConciliacaoItem
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro

class RepositoryExecucao(BaseRepository[ExecucaoPipeline]):
    
    def get_staging_pendentes(self, db: Session, exec_id: str) -> List[StagingRegistro]:

        """
        Retorna registros de staging pendentes com pessimistic lock para evitar race conditions.
        """
        return db.query(StagingRegistro).filter(
            StagingRegistro.execucao_id == exec_id, 
            StagingRegistro.processado == False
        ).with_for_update().all()

    def count_movimentacoes(self, db: Session, exec_id: str) -> int:
        execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
        if not execucao or not execucao.empresa_id: return 0
        return db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.empresa_id == execucao.empresa_id
        ).count()

    def count_candidates_by_status(self, db: Session, exec_id: str, status: str) -> int:
        return db.query(MatchCandidate).filter(
            MatchCandidate.execucao_id == exec_id,
            MatchCandidate.status == status
        ).count()
        
    def get_candidates(self, db: Session, exec_id: str, status: str) -> List[MatchCandidate]:
        return db.query(MatchCandidate).filter(
            MatchCandidate.execucao_id == exec_id,
            MatchCandidate.status == status
        ).all()

    def get_divergencies(self, db: Session, exec_id: str) -> List[MovimentacaoFinanceira]:
        execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
        if not execucao or not execucao.empresa_id: return []
        stmt = exists().where(
            MatchCandidate.movimentacao_financeira_id == MovimentacaoFinanceira.id
        ).where(
            MatchCandidate.status.in_(["APROVADO", "PENDENTE_REVISAO"])
        )
        return db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.empresa_id == execucao.empresa_id,
            MovimentacaoFinanceira.conciliada == False,
            not_(stmt)
        ).all()

    def get_conciliations(self, db: Session, exec_id: str) -> List[ConciliacaoItem]:
        execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
        if not execucao or not execucao.empresa_id: return []
        
        # Buscar todas as conciliações da empresa
        movs = db.query(MovimentacaoFinanceira.id).filter(
            MovimentacaoFinanceira.empresa_id == execucao.empresa_id
        ).all()
        mov_ids = [m[0] for m in movs]
        
        if not mov_ids:
            return []
            
        return db.query(ConciliacaoItem).options(
            joinedload(ConciliacaoItem.conciliacao),
            joinedload(ConciliacaoItem.movimentacao_financeira),
            joinedload(ConciliacaoItem.titulo),
            joinedload(ConciliacaoItem.lancamento)
        ).filter(
            ConciliacaoItem.movimentacao_financeira_id.in_(mov_ids)
        ).all()

execution_repo = RepositoryExecucao(ExecucaoPipeline)
