import pytest
from app.models.domain import TipoArquivo
from app.contexts.staging_ingestion.parsers.banco_inter import ExtratoInterAdapter
from app.contexts.staging_ingestion.parsers.razao_sucessor import RazaoSucessorAdapter
from app.contexts.staging_ingestion.parsers.pdf_generic import GenericPDFAdapter

def test_adapters_instantiation():
    inter_adapter = ExtratoInterAdapter()
    razao_adapter = RazaoSucessorAdapter()
    generic_pdf = GenericPDFAdapter()
    
    assert inter_adapter is not None
    assert razao_adapter is not None
    assert generic_pdf is not None

def test_inter_adapter_date_parsing():
    adapter = ExtratoInterAdapter()
    parsed = adapter._parse_portuguese_date("1 de Junho de 2026 Saldo do dia: R$ 34.255,05")
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 6
    assert parsed.day == 1
