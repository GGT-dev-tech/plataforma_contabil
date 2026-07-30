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

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_e2e_regression(db_session):
    # 1. Carrega as fixtures de Produção
    path_despesas = "tests/fixtures/production_sample/Despesas 06-2026.xlsx"
    path_sci = "tests/fixtures/production_sample/Razão SUCESSOR.xlsx"
    path_inter = "tests/fixtures/production_sample/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
    
    # 2. Ingestão
    ExcelDespesasParser().execute(path_despesas, TipoArquivo.DESPESA, db_session)
    SciRazaoParser().execute(path_sci, TipoArquivo.RAZAO, db_session)
    ExtratoInterParser().execute(path_inter, TipoArquivo.EXTRATO, db_session)
    
    # 3. Enrichment
    movs = db_session.query(MovimentacaoBancaria).all()
    parcelas = db_session.query(ParcelaDespesa).all()
    fornecedores = {f.id: f for f in db_session.query(Fornecedor).all()}
    EnrichmentService.enrich_movimentacoes(movs)
    EnrichmentService.enrich_parcelas(parcelas, fornecedores)
    
    # 4. Engine
    orchestrator = MatchOrchestrator(db_session)
    stats = orchestrator.run_pipeline()
    
    # 5. Golden Dataset Assertions
    golden_path = "tests/golden/expected_matches.json"
    with open(golden_path, 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
        
    expected_matches = golden_data["matches"]
    
    # Precisamos ter o mesmo número exato de conciliações
    assert len(orchestrator.reconciliation_log) == len(expected_matches), \
        f"Quebra de Regressão: Esperava {len(expected_matches)} matches, obteve {len(orchestrator.reconciliation_log)}"
        
    # Como não temos os UUIDs hardcoded, vamos parear as movimentações pela Descrição (única no contexto do extrato teste) e parcela_valor
    generated_map = {}
    for r in orchestrator.reconciliation_log:
        key = f"{r['mov_desc']}||{float(r['parcela_valor'])}"
        generated_map[key] = r
        
    for expected in expected_matches:
        key = f"{expected['mov_desc']}||{float(expected['parcela_valor'])}"
        assert key in generated_map, f"Quebra de Regressão: Match {key} desapareceu!"
        
        gen = generated_map[key]
        
        # Validar Status e Score
        assert gen['status'] == expected['status'], f"Status mudou para {key}"
        assert abs(gen['score'] - expected['score']) < 0.001, f"Score mudou para {key}"
        
        # Validar as Regras e sub-scores provando o Explainability
        gen_rules = {r['nome']: r for r in gen['regras']}
        for exp_rule in expected['regras']:
            r_name = exp_rule['nome']
            assert r_name in gen_rules, f"Regra {r_name} sumiu do explainability de {key}"
            assert abs(gen_rules[r_name]['score'] - exp_rule['score']) < 0.001, f"Sub-score da regra {r_name} mudou em {key}"
            
    # Validar se o db tem a persistencia correta (snapshot behaviour)
    from app.models.domain import ConciliacaoExplicacao, Conciliacao, MatchCandidate, StatusCandidato
    
    db_conciliacoes_auto = db_session.query(Conciliacao).all()
    db_candidatos_pendentes = db_session.query(MatchCandidate).filter(MatchCandidate.status == StatusCandidato.PENDENTE_REVISAO).all()
    
    # O Motor agora salva apenas 5 APROVADOS como Conciliacao e deixa 3 como MatchCandidate pendentes
    assert (len(db_conciliacoes_auto) + len(db_candidatos_pendentes)) == len(expected_matches)
    
    db_explicacoes = db_session.query(ConciliacaoExplicacao).all()
    assert len(db_explicacoes) > 0, "Explainability nao foi salva no DB!"
    
    # 6. Golden Dataset Macro Statistics Assertions
    stats_path = "tests/golden/expected_statistics.json"
    with open(stats_path, 'r', encoding='utf-8') as f:
        expected_stats = json.load(f)
        
    assert stats['matches_automaticos'] == expected_stats['matches_automaticos']
    assert stats['matches_revisao'] == expected_stats['matches_revisao']
    assert stats['divergencias'] == expected_stats['divergencias']
    assert stats['candidatos_avaliados'] == expected_stats['candidatos_avaliados']
