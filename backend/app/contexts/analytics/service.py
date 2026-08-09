from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from app.models.obra import Obra
from app.models.documento_fiscal import DocumentoFiscalV2

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_resumo_retencoes(self, empresa_id: str) -> Dict[str, float]:
        """
        Retorna a soma total das retenções para uma empresa,
        idealmente podendo ser filtrada por mês (aqui pegamos o total).
        """
        resultado = self.db.query(
            func.sum(DocumentoFiscalV2.iss_valor).label("total_iss"),
            func.sum(DocumentoFiscalV2.inss_valor).label("total_inss"),
            func.sum(DocumentoFiscalV2.ir_valor).label("total_ir"),
            func.sum(DocumentoFiscalV2.csll_valor).label("total_csll")
        ).filter(DocumentoFiscalV2.empresa_id == empresa_id).first()
        
        return {
            "iss": float(resultado.total_iss or 0),
            "inss": float(resultado.total_inss or 0),
            "ir": float(resultado.total_ir or 0),
            "csll": float(resultado.total_csll or 0)
        }
        
    def get_obras_por_regime(self, empresa_id: str) -> List[Dict[str, Any]]:
        """
        Retorna o número de obras agrupado por regime tributário (RET vs NORMAL).
        """
        resultados = self.db.query(
            Obra.regime_tributario,
            func.count(Obra.id).label("quantidade")
        ).filter(
            Obra.empresa_id == empresa_id,
            Obra.status == "ATIVO"
        ).group_by(Obra.regime_tributario).all()
        
        return [
            {"regime": r.regime_tributario, "quantidade": r.quantidade} 
            for r in resultados
        ]
        
    def get_evolucao_documentos(self, empresa_id: str) -> List[Dict[str, Any]]:
        """
        Retorna a evolução do valor bruto dos documentos por data de emissão.
        """
        # Em SQLite não tem func.date_trunc, então vamos simplificar para agrupar pela data exata, 
        # mas como estamos no Postgres, date_trunc("month", data_emissao) funcionaria.
        # Vamos agrupar de forma simplificada por data de emissão
        resultados = self.db.query(
            DocumentoFiscalV2.data_emissao,
            func.sum(DocumentoFiscalV2.valor_bruto).label("total")
        ).filter(
            DocumentoFiscalV2.empresa_id == empresa_id,
            DocumentoFiscalV2.data_emissao != None
        ).group_by(
            DocumentoFiscalV2.data_emissao
        ).order_by(
            DocumentoFiscalV2.data_emissao
        ).all()
        
        # Agrupa por mês para o chart do Recharts
        evolucao_por_mes = {}
        for r in resultados:
            if not r.data_emissao:
                continue
            mes_ano = r.data_emissao.strftime("%m/%Y")
            evolucao_por_mes[mes_ano] = evolucao_por_mes.get(mes_ano, 0) + float(r.total or 0)
            
        lista_final = [{"name": mes, "valor": val} for mes, val in evolucao_por_mes.items()]
        return lista_final
