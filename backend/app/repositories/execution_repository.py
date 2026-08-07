from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import not_, exists
from app.repositories.base import BaseRepository
from app.models.domain import ExecucaoPipeline, StagingRegistro, MovimentacaoBancaria, MatchCandidate, ConciliacaoItem, ParcelaDespesa

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
        return db.query(MovimentacaoBancaria).filter(
            MovimentacaoBancaria.execucao_id == exec_id
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

    def get_divergencies(self, db: Session, exec_id: str) -> List[MovimentacaoBancaria]:
        stmt = exists().where(
            MatchCandidate.movimentacao_id == MovimentacaoBancaria.id
        ).where(
            MatchCandidate.status.in_(["APROVADO", "PENDENTE_REVISAO"])
        )
        return db.query(MovimentacaoBancaria).filter(
            MovimentacaoBancaria.execucao_id == exec_id,
            not_(stmt)
        ).all()

    def get_conciliations(self, db: Session, exec_id: str) -> List[ConciliacaoItem]:
        movs = db.query(MovimentacaoBancaria).filter(
            MovimentacaoBancaria.execucao_id == exec_id
        ).all()
        mov_ids = [m.id for m in movs]
        
        if not mov_ids:
            return []
            
        return db.query(ConciliacaoItem).options(
            joinedload(ConciliacaoItem.conciliacao),
            joinedload(ConciliacaoItem.movimentacao),
            joinedload(ConciliacaoItem.parcela).joinedload(ParcelaDespesa.fornecedor),
            joinedload(ConciliacaoItem.lancamento)
        ).filter(
            ConciliacaoItem.movimentacao_id.in_(mov_ids)
        ).all()

execution_repo = RepositoryExecucao(ExecucaoPipeline)
