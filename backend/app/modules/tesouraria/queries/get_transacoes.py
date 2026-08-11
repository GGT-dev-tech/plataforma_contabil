from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any

class GetTransacoesQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str, conta_id: Optional[str] = None) -> List[Dict[str, Any]]:
        # Reduz as consultas N+1 executando um JOIN direto
        sql = """
            SELECT 
                t.id,
                t.conta_bancaria_id,
                c.descricao as conta_descricao,
                t.data_transacao,
                t.tipo,
                t.valor,
                t.descricao
            FROM tesouraria_transacoes t
            INNER JOIN tesouraria_contas c ON c.id = t.conta_bancaria_id
        """
        params = {}
        where_clauses = []
        
        if tenant_id:
            where_clauses.append("t.empresa_id = :tenant_id")
            params["tenant_id"] = tenant_id
            
        if conta_id:
            where_clauses.append("t.conta_bancaria_id = :conta_id")
            params["conta_id"] = conta_id
            
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
            
        sql += " ORDER BY t.data_transacao DESC LIMIT 100"
        
        results = db.execute(text(sql), params).fetchall()
        
        return [
            {
                "id": str(row.id),
                "conta_bancaria_id": str(row.conta_bancaria_id),
                "conta_descricao": row.conta_descricao,
                "data_transacao": row.data_transacao.isoformat(),
                "tipo": row.tipo,
                "valor": float(row.valor),
                "descricao": row.descricao
            }
            for row in results
        ]
