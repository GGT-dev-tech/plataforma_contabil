import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.parsers.excel.razao_sci_parser import SciRazaoParser
from app.models.domain import LancamentoContabil, ContaContabil, ImportacaoArquivo, TipoArquivo

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_sci_parser(db_session):
    parser = SciRazaoParser()
    file_path = "../Razão SUCESSOR.xlsx"
    assert os.path.exists(file_path), f"Arquivo de teste não encontrado: {file_path}"
    
    # Executa pipeline
    report = parser.execute(file_path, TipoArquivo.RAZAO, db_session)
    
    # Assertions do Relatório
    assert report.status == "SUCESSO", f"Parser falhou: {report.errors}"
    assert report.metrics.linhas_lidas > 0
    assert report.metrics.linhas_validas > 0
    
    # Validações no Canonical
    lancamentos = db_session.query(LancamentoContabil).all()
    contas = db_session.query(ContaContabil).all()
    
    assert len(lancamentos) > 0, "Deveria ter carregado lançamentos contábeis"
    assert len(contas) > 0, "Deveria ter carregado contas contábeis"
    
    # Verifica o componente de propagação de data (Date Propagation)
    for lanc in lancamentos:
        assert lanc.data is not None, f"Lançamento {lanc.chave_origem_sci} ficou sem data"
        
    # Verifica o componente de detecção de conta (Section Detector)
    for lanc in lancamentos:
        assert lanc.conta_contabil_id is not None
        
    # Verifica importação (Idempotência/Auditoria)
    importacao = db_session.query(ImportacaoArquivo).first()
    assert importacao.quantidade_registros == report.metrics.linhas_validas
    assert importacao.hash_arquivo == report.metrics.hash_arquivo
