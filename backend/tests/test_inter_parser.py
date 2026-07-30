import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.parsers.excel.extrato_inter_parser import ExtratoInterParser
from app.models.domain import MovimentacaoBancaria, ImportacaoArquivo, TipoArquivo

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_inter_parser(db_session):
    parser = ExtratoInterParser()
    file_path = "../Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
    assert os.path.exists(file_path), f"Arquivo de teste não encontrado: {file_path}"
    
    # Executa pipeline
    report = parser.execute(file_path, TipoArquivo.EXTRATO, db_session)
    
    # Assertions do Relatório
    assert report.status == "SUCESSO", f"Parser falhou: {report.errors}"
    assert report.metrics.linhas_lidas > 0
    assert report.metrics.linhas_validas > 0
    
    # Validações no Canonical
    movimentacoes = db_session.query(MovimentacaoBancaria).all()
    assert len(movimentacoes) > 0, "Deveria ter carregado movimentacoes bancarias"
    
    # Verifica propagacao de data e extração de codigo_cp
    cp_found = False
    for mov in movimentacoes:
        assert mov.data is not None
        assert mov.valor > 0
        if mov.codigo_cp:
            cp_found = True
            
    assert cp_found, "O TransactionDetector deveria ter achado pelo menos um 'Cp :'"
