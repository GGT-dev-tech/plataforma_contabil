from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

class GetSpedStatusQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str, job_id: str) -> Dict[str, Any]:
        sql = """
            SELECT 
                id,
                status,
                arquivo_url,
                log_erros
            FROM obrigacoes_acessorias_jobs
            WHERE id = :job_id
        """
        params = {"job_id": job_id}
        
        # Blindagem Multi-Tenant: um usuário não consegue consultar um Job de outra empresa
        if tenant_id:
            sql += " AND empresa_id = :tenant_id"
            params["tenant_id"] = tenant_id
            
        result = db.execute(text(sql), params).fetchone()
        
        if not result:
            return None
            
        return {
            "job_id": str(result.id),
            "status": result.status,
            "arquivo_url": result.arquivo_url,
            "log_erros": result.log_erros
        }
