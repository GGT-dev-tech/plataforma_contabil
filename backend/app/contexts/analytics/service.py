from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
import datetime

from app.models.obra import Obra
from app.models.documento_fiscal import DocumentoFiscalV2
from app.models.financeiro import TituloFinanceiro, TipoTitulo
from app.models.crm import PropostaVenda, StatusProposta
from app.models.tesouraria import TesourariaContaBancaria

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_resumo_retencoes(self, empresa_id: str) -> Dict[str, float]:
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
        
    def get_dashboard_geral(self, empresa_id: str) -> Dict[str, Any]:
        # 1. Saldo Consolidado em Caixa
        saldo_caixa = self.db.query(func.sum(TesourariaContaBancaria.saldo_atual)).filter(
            TesourariaContaBancaria.empresa_id == empresa_id
        ).scalar() or 0.0

        # 2. Receitas e Despesas (Mês Atual Simplificado)
        # Em SQLite isso pegaria tudo. Num BD real, faríamos um filtro de mês.
        receitas = self.db.query(func.sum(TituloFinanceiro.valor)).filter(
            TituloFinanceiro.empresa_id == empresa_id,
            TituloFinanceiro.tipo == TipoTitulo.RECEITA
        ).scalar() or 0.0
        
        despesas = self.db.query(func.sum(TituloFinanceiro.valor)).filter(
            TituloFinanceiro.empresa_id == empresa_id,
            TituloFinanceiro.tipo == TipoTitulo.DESPESA
        ).scalar() or 0.0

        # 3. VGV (Valor Geral de Vendas) de Propostas Aprovadas
        vgv = self.db.query(func.sum(PropostaVenda.valor_negociado)).filter(
            PropostaVenda.empresa_id == empresa_id,
            PropostaVenda.status == StatusProposta.APROVADA
        ).scalar() or 0.0

        return {
            "saldo_consolidado": float(saldo_caixa),
            "total_receitas": float(receitas),
            "total_despesas": float(despesas),
            "vgv_aprovado": float(vgv),
            "lucro_operacional": float(receitas - despesas)
        }
