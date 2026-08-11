from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any

class GetPropostasQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str, obra_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                p.id,
                p.obra_id,
                p.cliente_id,
                c.nome as cliente_nome,
                p.valor_negociado,
                p.unidade_descricao,
                p.status,
                p.data_proposta,
                p.notas
            FROM propostas_venda p
            INNER JOIN clientes c ON c.id = p.cliente_id
        """
        params = {}
        where_clauses = []
        
        if tenant_id:
            where_clauses.append("p.empresa_id = :tenant_id")
            params["tenant_id"] = tenant_id
            
        if obra_id:
            where_clauses.append("p.obra_id = :obra_id")
            params["obra_id"] = obra_id
            
        if status:
            where_clauses.append("p.status = :status")
            params["status"] = status
            
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
            
        sql += " ORDER BY p.data_proposta DESC"
        
        results = db.execute(text(sql), params).fetchall()
        
        return [
            {
                "id": str(row.id),
                "obra_id": str(row.obra_id),
                "cliente_id": str(row.cliente_id),
                "cliente_nome": row.cliente_nome,
                "valor_negociado": float(row.valor_negociado),
                "unidade_descricao": row.unidade_descricao,
                "status": row.status,
                "data_proposta": row.data_proposta.isoformat(),
                "notas": row.notas
            }
            for row in results
        ]
