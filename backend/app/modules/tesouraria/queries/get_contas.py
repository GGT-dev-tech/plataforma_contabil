from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any

class GetContasQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str) -> List[Dict[str, Any]]:
        # O Admin poderá ver de todas as empresas (se passarmos tenant_id=None ou ignorarmos o filtro).
        # Para rotas seguras, usamos WHERE.
        sql = """
            SELECT 
                id,
                banco,
                agencia,
                conta,
                descricao,
                saldo_atual
            FROM tesouraria_contas
        """
        params = {}
        
        if tenant_id:
            sql += " WHERE empresa_id = :tenant_id"
            params["tenant_id"] = tenant_id
            
        sql += " ORDER BY descricao ASC"
        
        results = db.execute(text(sql), params).fetchall()
        
        return [
            {
                "id": str(row.id),
                "banco": row.banco,
                "agencia": row.agencia,
                "conta": row.conta,
                "descricao": row.descricao,
                "saldo_atual": float(row.saldo_atual)
            }
            for row in results
        ]
