import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import (
    StagingRegistro, TipoStaging, Receita, Fornecedor
)
from app.models.financeiro import TituloFinanceiro, TipoTitulo, MovimentacaoFinanceira, TipoMovimentacao

from app.contexts.matching_auditing.engine.tax_engine import TaxEngine

class StagingService:
    def __init__(self, db: Session, regime_tributario: str = "LUCRO_PRESUMIDO"):
        self.db = db
        self.tax_engine = TaxEngine(regime_tributario=regime_tributario)

    def process_staging_items(self, exec_id: str, staging_items: List[StagingRegistro]) -> Dict[str, Any]:
        tax_summary = {
            "total_receitas": 0.0, 
            "total_despesas": 0.0, 
            "impostos_devidos": 0.0, 
            "impostos_retidos": 0.0
        }

        for item in staging_items:
            self._process_item(exec_id, item, tax_summary)
            item.processado = True

        return {
            "tax_summary": tax_summary
        }

    def _process_item(self, exec_id: str, item: StagingRegistro, tax_summary: Dict[str, float]):
        if item.tipo == TipoStaging.RECEITA:
            self._process_receita(exec_id, item, tax_summary)
        elif item.tipo == TipoStaging.DESPESA:
            self._process_despesa(exec_id, item, tax_summary)
        elif item.tipo in [TipoStaging.EXTRATO, TipoStaging.DINHEIRO]:
            self._process_movimentacao(exec_id, item)

    def _process_receita(self, exec_id: str, item: StagingRegistro, tax_summary: Dict[str, float]):
        rec = Receita(
            id=str(uuid.uuid4()), 
            execucao_id=exec_id, 
            cliente_nome=item.entidade_nome or "Cliente Não Identificado",
            descricao=item.descricao, 
            valor_total=item.valor, 
            data_emissao=item.data, 
            forma_pagamento=item.forma_pagamento,
            conta_destino=item.conta_destino
        )
        self.db.add(rec)
        taxes = self.tax_engine.process_operation("RECEITA", item.valor)
        tax_summary["total_receitas"] += float(item.valor)
        tax_summary["impostos_devidos"] += sum(float(t.valor_tributo) for t in taxes if t.tipo == "DEVIDO")

    def _process_despesa(self, exec_id: str, item: StagingRegistro, tax_summary: Dict[str, float]):
        forn = None
        if item.entidade_nome:
            forn = self.db.query(Fornecedor).filter(Fornecedor.nome == item.entidade_nome).first()
            if not forn:
                forn = Fornecedor(
                    id=uuid.uuid4(), 
                    cnpj_cpf=item.cnpj_cpf or "00000000000000", 
                    nome=item.entidade_nome, 
                    nome_normalizado=item.entidade_nome.upper()
                )
                self.db.add(forn)
                self.db.flush()

        # Criação do Título (substituindo Despesa/ParcelaDespesa)
        titulo = TituloFinanceiro(
            id=str(uuid.uuid4()), 
            empresa_id=item.empresa_id,
            tipo=TipoTitulo.PAGAR,
            descricao=item.descricao,
            fornecedor_cliente_nome=item.entidade_nome,
            fornecedor_cliente_cnpj_cpf=item.cnpj_cpf,
            valor_nominal=float(item.valor),
            data_emissao=item.data,
            data_vencimento=item.data,
            gerado_automaticamente=True,
            categoria=item.categoria
        )
        self.db.add(titulo)
        taxes = self.tax_engine.process_operation("DESPESA", item.valor)
        tax_summary["total_despesas"] += float(item.valor)
        tax_summary["impostos_retidos"] += sum(float(t.valor_tributo) for t in taxes if t.tipo == "RETIDO")

    def _process_movimentacao(self, exec_id: str, item: StagingRegistro):
        mov = MovimentacaoFinanceira(
            id=str(uuid.uuid4()), 
            empresa_id=item.empresa_id,
            tipo=TipoMovimentacao.ENTRADA if item.valor > 0 else TipoMovimentacao.SAIDA,
            data_transacao=item.data, 
            descricao_extrato=item.descricao,
            valor=float(item.valor), 
            conciliada=False,
            categoria=item.categoria
        )
        self.db.add(mov)

staging_service = StagingService
