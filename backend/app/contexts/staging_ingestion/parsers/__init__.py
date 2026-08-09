from .base import ImportAdapter
from .factory import ParserFactory
from .banco_inter import ExtratoInterAdapter
from .despesas_erp import DespesasERPAdapter
from .razao_sucessor import RazaoSucessorAdapter
from .pdf_generic import GenericPDFAdapter
from .xml_generic import GenericXMLAdapter
from .nfe_xml import NFeXMLAdapter
from .generic_spreadsheet import GenericSpreadsheetAdapter

# Registrar os adapters
ParserFactory.register(ExtratoInterAdapter())
ParserFactory.register(DespesasERPAdapter())
ParserFactory.register(RazaoSucessorAdapter())
ParserFactory.register(GenericPDFAdapter())
ParserFactory.register(NFeXMLAdapter())    # Prioridade sobre GenericXMLAdapter
ParserFactory.register(GenericXMLAdapter())  # Fallback XML genérico
# Generic Spreadsheet deve ser o último para atuar como fallback de planilhas
ParserFactory.register(GenericSpreadsheetAdapter())

__all__ = [
    "ImportAdapter",
    "ParserFactory"
]
