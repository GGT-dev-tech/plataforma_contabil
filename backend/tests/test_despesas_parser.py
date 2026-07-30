import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.parsers.excel.despesas_parser import ExcelDespesasParser
from app.models.domain import Despesa, ParcelaDespesa, Fornecedor, Projeto, ImportacaoArquivo, TipoArquivo

# DB Setup for tests
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_despesas_parser(db_session):
    # Setup
    parser = ExcelDespesasParser()
    # Pega o arquivo real na raiz do projeto (caminho relativo)
    file_path = "../Despesas 06-2026.xlsx"
    assert os.path.exists(file_path), f"Arquivo de teste não encontrado: {file_path}"
    
    # 1. Pipeline Execution
    result = parser.execute(file_path, TipoArquivo.DESPESA, db_session)
    
    # Validações de pipeline
    assert result.status == "SUCESSO"
    assert result.metrics.linhas_lidas > 0
    
    # 2. Assertions no Banco (Canonical)
    despesas = db_session.query(Despesa).all()
    parcelas = db_session.query(ParcelaDespesa).all()
    fornecedores = db_session.query(Fornecedor).all()
    projetos = db_session.query(Projeto).all()
    importacao = db_session.query(ImportacaoArquivo).first()
    
    # Validações
    assert len(despesas) > 0, "Deveria ter carregado despesas"
    assert len(parcelas) > 0, "Deveria ter carregado parcelas"
    assert len(fornecedores) > 0, "Deveria ter criado fornecedores"
    
    # Valida regras de UUID
    assert despesas[0].id_uuid_origem is not None, "UUID original da despesa deve ser preservado"
    assert parcelas[0].id_parcela_origem is not None, "UUID original da parcela deve ser preservado"
    
    # Valida regra de fornecedor normalizado
    fn_teste = [f for f in fornecedores if "BH MATERIAIS DE CONSTRUCAO" in f.nome]
    if fn_teste:
        assert fn_teste[0].nome_normalizado == "BH MATERIAIS CONSTRUCAO"
        
    # Valida datas convertidas
    assert parcelas[0].data_vencimento is not None
    
    # Valida sinal positivo
    assert despesas[0].valor_total >= 0, "A convenção definiu sinal positivo no canonical"
    
    # Valida auditoria
    assert importacao is not None
    assert importacao.quantidade_registros == len(parcelas)
    assert importacao.erros_encontrados == 0
    assert despesas[0].arquivo_origem == importacao.id
