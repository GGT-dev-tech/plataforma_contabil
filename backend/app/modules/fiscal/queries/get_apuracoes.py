from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from app.models.fiscal import ApuracaoFiscal, DetalheImposto

class GetApuracoesQueryHandler:
    @staticmethod
    def execute(db: Session, tenant_id: str, competencia: Optional[str] = None) -> List[Dict[str, Any]]:
        # O Query Handler pula a complexidade do ORM e resolve tudo em SQL direto.
        # No caso, usamos SQLAlchemy Core para buscar apuracoes + detalhes em uma query só (JOIN),
        # ou duas queries se for mais rápido.
        # Para simplificar e acelerar a migração com Strangler Fig, 
        # faremos uma query crua montando o objeto.
        
        sql = """
            SELECT 
                a.id as apuracao_id,
                a.empresa_id,
                a.competencia,
                a.faturamento_total,
                a.imposto_devido,
                d.id as detalhe_id,
                d.tipo_imposto,
                d.base_de_calculo,
                d.aliquota,
                d.valor_apurado,
                d.valor_retido,
                d.valor_a_pagar
            FROM apuracoes_fiscais a
            LEFT JOIN detalhes_impostos d ON d.apuracao_id = a.id
            WHERE a.empresa_id = :tenant_id
        """
        params = {"tenant_id": tenant_id}
        
        if competencia:
            sql += " AND a.competencia = :competencia"
            params["competencia"] = competencia
            
        sql += " ORDER BY a.competencia DESC"
        
        results = db.execute(text(sql), params).fetchall()
        
        # Agrupar os resultados
        apuracoes_map = {}
        for row in results:
            a_id = str(row.apuracao_id)
            if a_id not in apuracoes_map:
                apuracoes_map[a_id] = {
                    "id": a_id,
                    "empresa_id": str(row.empresa_id),
                    "competencia": row.competencia,
                    "faturamento_total": float(row.faturamento_total),
                    "imposto_devido": float(row.imposto_devido),
                    "detalhes": []
                }
                
            if row.detalhe_id:
                apuracoes_map[a_id]["detalhes"].append({
                    "id": str(row.detalhe_id),
                    "tipo_imposto": row.tipo_imposto,
                    "base_de_calculo": float(row.base_de_calculo),
                    "aliquota": float(row.aliquota),
                    "valor_apurado": float(row.valor_apurado),
                    "valor_retido": float(row.valor_retido),
                    "valor_a_pagar": float(row.valor_a_pagar)
                })
                
        return list(apuracoes_map.values())
