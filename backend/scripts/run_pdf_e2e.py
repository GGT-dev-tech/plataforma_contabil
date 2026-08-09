import os
import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.domain import ExecucaoPipeline, StatusExecucao, StagingRegistro, MovimentacaoBancaria, ParcelaDespesa, Fornecedor
from app.contexts.staging_ingestion.parsers.pdf_generic import GenericPDFAdapter
from app.contexts.staging_ingestion.service import StagingService
from app.services.enrichment import EnrichmentService
from app.contexts.matching_auditing.engine.core import MatchOrchestrator

def main():
    print("Inicializando banco de dados em memória para teste E2E com PDFs...")
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    exec_id = str(uuid.uuid4())
    execucao = ExecucaoPipeline(id=exec_id, status=StatusExecucao.CRIADA)
    db.add(execucao)
    db.commit()
    
    # 1. Ingestão (Staging)
    print("1. Ingestão de Arquivos PDF (Extrato e Razão)")
    adapter = GenericPDFAdapter()
    
    extrato_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_data/extrato_sample.pdf"))
    razao_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_data/razao_sample.pdf"))
    
    adapter.parse(extrato_path, db, exec_id)
    adapter.parse(razao_path, db, exec_id)
    
    registros_staging = db.query(StagingRegistro).filter_by(execucao_id=exec_id).all()
    print(f" -> {len(registros_staging)} registros extraídos para Staging.")
    
    # 2. Processamento Staging -> Domínio
    print("2. Processamento (Staging -> Normalização)")
    service = StagingService(db)
    service.process_staging_items(exec_id, registros_staging)
    db.commit()
    
    movs = db.query(MovimentacaoBancaria).filter_by(execucao_id=exec_id).all()
    parcelas = db.query(ParcelaDespesa).all()
    print(f" -> {len(movs)} Movimentações geradas e {len(parcelas)} Parcelas de Despesa geradas.")
    
    # 3. Enrichment
    print("3. Enriquecimento de Dados")
    fornecedores = {f.id: f for f in db.query(Fornecedor).all()}
    EnrichmentService.enrich_movimentacoes(movs)
    EnrichmentService.enrich_parcelas(parcelas, fornecedores)
    print(" -> Features de Enrichment extraídas (CNPJ, Palavras-chave, etc).")
    
    # 4. Engine de Conciliação
    print("4. Executando o Motor de Conciliação")
    orchestrator = MatchOrchestrator(db, execucao_id=exec_id)
    stats = orchestrator.run_pipeline()
    
    print("\n========= RESULTADOS DA CONCILIAÇÃO =========")
    print(f"Total de Matches Automáticos: {stats['matches_automaticos']}")
    print(f"Matches Pendentes de Revisão: {stats['matches_revisao']}")
    print(f"Movimentações Restantes: {stats['divergencias']}")
    
    print("\n--- Log de Reconciliação ---")
    for log in orchestrator.reconciliation_log:
        p_val = log.get('parcela_valor', 'N/A')
        print(f"MATCH: {log.get('mov_desc')} ({log.get('mov_valor')}) <-> {log.get('fornecedor_nome', 'Desconhecido')} ({p_val})")
        print(f"  Score: {log.get('score', 0):.2f}")
        print(f"  Status: {log.get('status')}")
        for rule in log.get('regras', []):
            print(f"    - {rule.get('nome')}: {rule.get('score', 0):.2f} ({rule.get('motivo')})")
        print()

if __name__ == "__main__":
    main()
