from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.fiscal import ApuracaoFiscal
from app.models.empresa_fiscal import EmpresaFiscal

class TaxStrategy(ABC):
    """
    Interface base para estratégias de cálculo tributário.
    """
    
    def __init__(self, db: Session, empresa: EmpresaFiscal):
        self.db = db
        self.empresa = empresa

    @abstractmethod
    def apurar_impostos(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        """
        Recebe a competência (ex: 2026-08) e os dados do faturamento
        e retorna uma ApuracaoFiscal (com os DetalheImposto preenchidos e não comitados).
        """
        pass
