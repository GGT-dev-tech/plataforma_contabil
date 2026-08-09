import pytest
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.domain import TipoStaging, ExecucaoPipeline, StagingRegistro, StatusExecucao
from app.contexts.staging_ingestion.parsers.pdf_generic import GenericPDFAdapter

@pytest.fixture
def memory_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_pdf_extrato_parsing(memory_db_session):
    exec_id = str(uuid.uuid4())
    execucao = ExecucaoPipeline(id=exec_id, status=StatusExecucao.CRIADA)
    memory_db_session.add(execucao)
    memory_db_session.commit()
    
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_data/extrato_sample.pdf"))
    adapter = GenericPDFAdapter()
    
    assert adapter.can_parse(file_path, None) is True
    success = adapter.parse(file_path, memory_db_session, exec_id)
    assert success is True
    
    registros = memory_db_session.query(StagingRegistro).filter_by(execucao_id=exec_id).all()
    assert len(registros) == 4
    
    # Check if all are EXTRATO
    assert all(r.tipo == TipoStaging.EXTRATO for r in registros)
    
    # Check values and negatives
    # 132.500,00 -> -132500.0
    vals = [r.valor for r in registros]
    assert -132500.0 in vals
    assert -45000.0 in vals
    assert -12000.0 in vals
    assert -150.0 in vals
    
    # Check descriptions
    descrs = [r.descricao for r in registros]
    assert any("UP ESQUADRIAS" in d for d in descrs)
    assert any("MADEIREIRA SAO JOAO" in d for d in descrs)
    assert any("CIMENTO POTY" in d for d in descrs)

def test_pdf_razao_parsing(memory_db_session):
    exec_id = str(uuid.uuid4())
    execucao = ExecucaoPipeline(id=exec_id, status=StatusExecucao.CRIADA)
    memory_db_session.add(execucao)
    memory_db_session.commit()
    
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_data/razao_sample.pdf"))
    adapter = GenericPDFAdapter()
    
    assert adapter.can_parse(file_path, None) is True
    success = adapter.parse(file_path, memory_db_session, exec_id)
    assert success is True
    
    registros = memory_db_session.query(StagingRegistro).filter_by(execucao_id=exec_id).all()
    assert len(registros) == 4
    
    # Check if all are DESPESA (since the filename contains "razao")
    assert all(r.tipo == TipoStaging.DESPESA for r in registros)
    
    # Check values and negatives
    vals = [r.valor for r in registros]
    assert -132500.0 in vals
    assert -45000.0 in vals
    
    # Check descriptions
    descrs = [r.descricao for r in registros]
    assert any("UP ESQUADRIAS" in d for d in descrs)
    assert any("MADEIREIRA SAO JOAO" in d for d in descrs)
