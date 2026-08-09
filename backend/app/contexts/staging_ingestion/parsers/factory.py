import logging
from typing import List, Optional, Dict, Any
from app.models.domain import TipoArquivo
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class ParserFactory:
    _adapters: List[ImportAdapter] = []

    @classmethod
    def register(cls, adapter: ImportAdapter):
        if adapter not in cls._adapters:
            cls._adapters.append(adapter)
            
    @classmethod
    def get_parser(cls, file_path: str, tipo_arquivo: TipoArquivo, import_config: Optional[Dict[str, Any]] = None) -> Optional[ImportAdapter]:
        # 1. Tentar usar o ConfigurableSpreadsheetParser se houver config específica para o cliente
        if import_config and tipo_arquivo.name in import_config:
            logger.info(f"Usando parser configurável para {tipo_arquivo.name}")
            from app.contexts.staging_ingestion.parsers.configurable_spreadsheet import ConfigurableSpreadsheetParser
            parser = ConfigurableSpreadsheetParser(import_config=import_config, tipo_arquivo=tipo_arquivo)
            if parser.can_parse(file_path, tipo_arquivo):
                return parser

        # 2. Fallback para os parsers heurísticos registrados
        for adapter in cls._adapters:
            try:
                if adapter.can_parse(file_path, tipo_arquivo):
                    return adapter
            except Exception as e:
                logger.warning(f"Erro ao verificar can_parse no adapter {adapter.__class__.__name__}: {e}")
                continue
        return None
