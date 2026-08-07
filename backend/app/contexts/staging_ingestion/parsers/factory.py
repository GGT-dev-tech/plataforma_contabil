import logging
from typing import List, Optional
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
    def get_parser(cls, file_path: str, tipo_arquivo: TipoArquivo) -> Optional[ImportAdapter]:
        for adapter in cls._adapters:
            try:
                if adapter.can_parse(file_path, tipo_arquivo):
                    return adapter
            except Exception as e:
                logger.warning(f"Erro ao verificar can_parse no adapter {adapter.__class__.__name__}: {e}")
                continue
        return None
