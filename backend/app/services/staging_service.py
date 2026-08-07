import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import (
    StagingRegistro, TipoStaging, Receita, ParcelaDespesa, 
    Despesa, Fornecedor, MovimentacaoBancaria, TipoMovimentacao
)
from app.engine.tax_engine import TaxEngine
from app.engine.core import MatchOrchestrator

class StagingService:
    def __init__(self, db: Session):
        self.db = db
        self.tax_engine = TaxEngine(regime_tributario="LUCRO_PRESUMIDO")

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

        self.db.commit()

        # Executar MatchOrchestrator
        orchestrator = MatchOrchestrator(self.db, execucao_id=exec_id)
        match_stats = orchestrator.run_pipeline()

        return {
            "tax_summary": tax_summary,
            "match_stats": match_stats
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

        desp = Despesa(
            id=uuid.uuid4(), 
            execucao_id=exec_id, 
            fornecedor_id=forn.id if forn else None,
            valor_total=item.valor, 
            data_emissao=item.data, 
            id_uuid_origem=str(uuid.uuid4())
        )
        self.db.add(desp)
        self.db.flush()

        parc = ParcelaDespesa(
            id=uuid.uuid4(), 
            despesa_id=desp.id, 
            numero_parcela=1, 
            valor=item.valor, 
            data_vencimento=item.data,
            id_parcela_origem=str(uuid.uuid4())
        )
        self.db.add(parc)
        taxes = self.tax_engine.process_operation("DESPESA", item.valor)
        tax_summary["total_despesas"] += float(item.valor)
        tax_summary["impostos_retidos"] += sum(float(t.valor_tributo) for t in taxes if t.tipo == "RETIDO")

    def _process_movimentacao(self, exec_id: str, item: StagingRegistro):
        mov = MovimentacaoBancaria(
            id=uuid.uuid4(), 
            execucao_id=exec_id, 
            data=item.data, 
            historico=item.descricao,
            valor=item.valor, 
            tipo=TipoMovimentacao.C if item.valor > 0 else TipoMovimentacao.D
        )
        self.db.add(mov)

staging_service = StagingService
