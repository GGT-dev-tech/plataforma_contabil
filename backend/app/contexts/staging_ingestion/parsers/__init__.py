from .base import ImportAdapter
from .factory import ParserFactory
from .banco_inter import ExtratoInterAdapter
from .despesas_erp import DespesasERPAdapter
from .razao_sucessor import RazaoSucessorAdapter

# Registrar os adapters
ParserFactory.register(ExtratoInterAdapter())
ParserFactory.register(DespesasERPAdapter())
ParserFactory.register(RazaoSucessorAdapter())

__all__ = [
    "ImportAdapter",
    "ParserFactory"
]
