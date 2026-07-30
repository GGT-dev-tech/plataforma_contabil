import pytest
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.domain import TipoArquivo, MovimentacaoBancaria, ParcelaDespesa, Fornecedor
from app.parsers.excel.despesas_parser import ExcelDespesasParser
from app.parsers.excel.razao_sci_parser import SciRazaoParser
from app.parsers.excel.extrato_inter_parser import ExtratoInterParser
from app.services.enrichment import EnrichmentService
from app.engine.core import MatchOrchestrator

def run_pipeline_in_memory():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    
    path_despesas = "tests/fixtures/production_sample/Despesas 06-2026.xlsx"
    path_sci = "tests/fixtures/production_sample/Razão SUCESSOR.xlsx"
    path_inter = "tests/fixtures/production_sample/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
    
    ExcelDespesasParser().execute(path_despesas, TipoArquivo.DESPESA, db_session)
    SciRazaoParser().execute(path_sci, TipoArquivo.RAZAO, db_session)
    ExtratoInterParser().execute(path_inter, TipoArquivo.EXTRATO, db_session)
    
    movs = db_session.query(MovimentacaoBancaria).all()
    parcelas = db_session.query(ParcelaDespesa).all()
    fornecedores = {f.id: f for f in db_session.query(Fornecedor).all()}
    EnrichmentService.enrich_movimentacoes(movs)
    EnrichmentService.enrich_parcelas(parcelas, fornecedores)
    
    orchestrator = MatchOrchestrator(db_session)
    stats = orchestrator.run_pipeline()
    
    # Extrair os logs e métricas ignorando timestamps/UUIDs
    reconciliation = []
    for r in orchestrator.reconciliation_log:
        r_clean = r.copy()
        # Remove UUIDs
        del r_clean['mov_id']
        del r_clean['parcela_id']
        reconciliation.append(r_clean)
        
    divergencias = []
    for d in orchestrator.divergencias_log:
        d_clean = d.copy()
        del d_clean['mov_id']
        divergencias.append(d_clean)
        
    candidates_discard = []
    for c in orchestrator.candidate_gen.discard_log + orchestrator.candidates_discard_engine_log:
        c_clean = c.copy()
        del c_clean['mov_id']
        del c_clean['parcela_id']
        candidates_discard.append(c_clean)
        
    db_session.close()
    return stats, reconciliation, divergencias, candidates_discard


def test_reproducibility_comparator():
    """
    Roda a pipeline inteira do zero duas vezes e aplica um comparator nas estruturas semânticas.
    Se qualquer match, divergencia, discard log ou score for diferente entre as rodadas, falha o teste.
    """
    
    # Run 1
    stats_1, rec_1, div_1, cand_1 = run_pipeline_in_memory()
    
    # Run 2
    stats_2, rec_2, div_2, cand_2 = run_pipeline_in_memory()
    
    # Asserts macro stats
    assert stats_1['matches_automaticos'] == stats_2['matches_automaticos']
    assert stats_1['matches_revisao'] == stats_2['matches_revisao']
    assert stats_1['divergencias'] == stats_2['divergencias']
    assert stats_1['candidatos_avaliados'] == stats_2['candidatos_avaliados']
    
    # Asserts reconciliation logs
    assert len(rec_1) == len(rec_2)
    # Sort just in case order is non-deterministic (it shouldn't be)
    rec_1 = sorted(rec_1, key=lambda x: x['mov_desc'])
    rec_2 = sorted(rec_2, key=lambda x: x['mov_desc'])
    
    for r1, r2 in zip(rec_1, rec_2):
        assert r1 == r2, f"Discrepância na Conciliação: {r1} != {r2}"
        
    # Asserts divergencias logs
    assert len(div_1) == len(div_2)
    div_1 = sorted(div_1, key=lambda x: x['historico'])
    div_2 = sorted(div_2, key=lambda x: x['historico'])
    for d1, d2 in zip(div_1, div_2):
        assert d1 == d2, f"Discrepância nas Divergências: {d1} != {d2}"
        
    # Asserts candidates discards
    assert len(cand_1) == len(cand_2)
