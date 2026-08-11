from sqlalchemy.orm import Session
from app.models.empresa_fiscal import EmpresaFiscal, RegimeTributario
from app.models.fiscal import ApuracaoFiscal
from typing import Dict, Any

from app.contexts.fiscal_engine.strategies.base import TaxStrategy
from app.contexts.fiscal_engine.strategies.mei_strategy import MeiStrategy
from app.contexts.fiscal_engine.strategies.simples_nacional_strategy import SimplesNacionalStrategy
from app.contexts.fiscal_engine.strategies.lucro_presumido_strategy import LucroPresumidoStrategy
from app.contexts.fiscal_engine.strategies.lucro_real_strategy import LucroRealStrategy

class TaxEngine:
    """
    Motor Fiscal.
    Utiliza o padrão Strategy para orquestrar o cálculo de impostos de acordo com o regime da empresa.
    """
    
    def __init__(self, db: Session, empresa: EmpresaFiscal):
        self.db = db
        self.empresa = empresa
        self.strategy = self._selecionar_strategy()
        
    def _selecionar_strategy(self) -> TaxStrategy:
        if self.empresa.regime_tributario == RegimeTributario.MEI:
            return MeiStrategy(self.db, self.empresa)
        elif self.empresa.regime_tributario == RegimeTributario.SIMPLES_NACIONAL:
            return SimplesNacionalStrategy(self.db, self.empresa)
        elif self.empresa.regime_tributario == RegimeTributario.LUCRO_PRESUMIDO:
            return LucroPresumidoStrategy(self.db, self.empresa)
        elif self.empresa.regime_tributario == RegimeTributario.LUCRO_REAL:
            return LucroRealStrategy(self.db, self.empresa)
        else:
            raise ValueError(f"Regime {self.empresa.regime_tributario} não suportado no momento.")
            
    def executar_calculo_mensal(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        """
        Executa a apuração e salva no banco de dados.
        """
        apuracao = self.strategy.apurar_impostos(competencia, dados_faturamento)
        self.db.add(apuracao)
        self.db.commit()
        self.db.refresh(apuracao)
        return apuracao
