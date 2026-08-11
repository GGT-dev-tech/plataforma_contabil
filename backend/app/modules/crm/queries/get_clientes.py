from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any

class GetClientesQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                id,
                nome,
                email,
                telefone,
                cpf_cnpj,
                renda_mensal
            FROM clientes
        """
        params = {}
        
        if tenant_id:
            sql += " WHERE empresa_id = :tenant_id"
            params["tenant_id"] = tenant_id
            
        sql += " ORDER BY nome ASC LIMIT 100"
        
        results = db.execute(text(sql), params).fetchall()
        
        return [
            {
                "id": str(row.id),
                "nome": row.nome,
                "email": row.email,
                "telefone": row.telefone,
                "cpf_cnpj": row.cpf_cnpj,
                "renda_mensal": float(row.renda_mensal) if row.renda_mensal else None
            }
            for row in results
        ]
