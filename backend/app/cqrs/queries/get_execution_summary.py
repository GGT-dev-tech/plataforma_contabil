from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict

class GetExecutionSummaryQueryHandler:
    """
    CQRS Query Handler para extrair métricas de dashboard usando SQL bruto,
    evitando N overheads do ORM e reduzindo de N requisições de Count para 1 única query rápida.
    """
    
    @staticmethod
    def execute(db: Session, exec_id: str) -> Dict[str, int]:
        query = text("""
            SELECT 
                (SELECT COUNT(1) FROM movimentacao_bancaria WHERE execucao_id = :exec_id) as total_movimentacoes,
                (SELECT COUNT(1) FROM match_candidate WHERE execucao_id = :exec_id AND status = 'APROVADO') as total_aprovados,
                (SELECT COUNT(1) FROM match_candidate WHERE execucao_id = :exec_id AND status = 'PENDENTE_REVISAO') as total_pendentes,
                (SELECT COUNT(1) FROM match_candidate WHERE execucao_id = :exec_id AND status = 'REJEITADO_PELO_MOTOR') as total_rejeitados
        """)
        
        # O fetchone vai retornar uma tupla ou row dict-like do banco
        result = db.execute(query, {"exec_id": exec_id}).mappings().first()
        
        if not result:
            return {
                "total_movimentacoes": 0,
                "total_aprovados": 0,
                "total_pendentes": 0,
                "total_rejeitados": 0
            }
            
        return dict(result)
