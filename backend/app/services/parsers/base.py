import abc
from typing import BinaryIO, List
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo

class ImportAdapter(abc.ABC):
    """
    Interface base para parsers de planilhas e extratos.
    Cada ERP ou formato de banco terá o seu próprio Adapter.
    """
    
    @abc.abstractmethod
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        """
        Retorna True se o adapter sabe como processar o arquivo.
        Isto pode ser feito lendo os headers do arquivo ou inferindo pelo nome.
        """
        pass
        
    @abc.abstractmethod
    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        """
        Processa o arquivo e salva no modelo canônico do banco de dados.
        Retorna True em caso de sucesso absoluto.
        """
        pass

    def _parse_date(self, val):
        import pandas as pd
        from datetime import datetime
        if pd.isna(val):
            return None
        if isinstance(val, datetime):
            return val.date()
        try:
            return pd.to_datetime(val, dayfirst=True).date()
        except:
            return None

    def _parse_float(self, val) -> float:
        import pandas as pd
        if pd.isna(val):
            return 0.0
        try:
            if isinstance(val, str):
                # Remove spaces, "R$", dots, replace comma with dot
                val = val.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".").strip()
            return float(val)
        except:
            return 0.0
