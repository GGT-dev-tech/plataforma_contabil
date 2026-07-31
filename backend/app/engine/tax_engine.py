from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

class TaxStrategy(ABC):
    @abstractmethod
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        pass

class PisCalculationStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        return round(base_amount * (rate / Decimal("100.0")), 2)

class CofinsCalculationStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        return round(base_amount * (rate / Decimal("100.0")), 2)

class IssCalculationStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        return round(base_amount * (rate / Decimal("100.0")), 2)

class IrpjLucroPresumidoStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        presumed_percentage = kwargs.get("presumed_percentage", Decimal("32.0"))
        base_calculo = base_amount * (presumed_percentage / Decimal("100.0"))
        return round(base_calculo * (rate / Decimal("100.0")), 2)

class CsllLucroPresumidoStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        presumed_percentage = kwargs.get("presumed_percentage", Decimal("32.0"))
        base_calculo = base_amount * (presumed_percentage / Decimal("100.0"))
        return round(base_calculo * (rate / Decimal("100.0")), 2)

class WithholdingCalculationStrategy(TaxStrategy):
    def calculate(self, base_amount: Decimal, rate: Decimal, **kwargs) -> Decimal:
        return round(base_amount * (rate / Decimal("100.0")), 2)

@dataclass
class TaxResult:
    imposto: str
    base_calculo: Decimal
    aliquota: Decimal
    valor_tributo: Decimal
    tipo: str # "DEVIDO" ou "RETIDO"

class TaxEngine:
    """
    Motor Tributário e Fiscal integrado da Plataforma Contábil (reaproveitado de CEDIPI-Shield).
    Calcula PIS, COFINS, ISS, IRPJ, CSLL e retenções na fonte para operações financeiras.
    """
    def __init__(self, regime_tributario: str = "LUCRO_PRESUMIDO"):
        self.regime_tributario = regime_tributario
        self.strategies: Dict[str, TaxStrategy] = {
            "PIS": PisCalculationStrategy(),
            "COFINS": CofinsCalculationStrategy(),
            "ISS": IssCalculationStrategy(),
            "IRPJ": IrpjLucroPresumidoStrategy(),
            "CSLL": CsllLucroPresumidoStrategy(),
            "IRRF": WithholdingCalculationStrategy()
        }
        # Alíquotas padrão por regime
        self.default_rates = {
            "PIS": Decimal("0.65") if regime_tributario == "LUCRO_PRESUMIDO" else Decimal("1.65"),
            "COFINS": Decimal("3.00") if regime_tributario == "LUCRO_PRESUMIDO" else Decimal("7.60"),
            "ISS": Decimal("5.00"),
            "IRPJ": Decimal("15.00"),
            "CSLL": Decimal("9.00"),
            "IRRF": Decimal("1.50")
        }

    def process_operation(self, tipo_operacao: str, valor: Decimal, aliquotas_custom: Optional[Dict[str, Decimal]] = None) -> List[TaxResult]:
        """
        Processa uma operação financeira (RECEITA ou DESPESA) e retorna a lista de impostos calculados.
        """
        rates = self.default_rates.copy()
        if aliquotas_custom:
            rates.update(aliquotas_custom)

        results = []

        if tipo_operacao.upper() in ["RECEITA", "FATURAMENTO"]:
            # Impostos diretos sobre receita
            pis = self.strategies["PIS"].calculate(valor, rates["PIS"])
            cofins = self.strategies["COFINS"].calculate(valor, rates["COFINS"])
            iss = self.strategies["ISS"].calculate(valor, rates["ISS"])
            irpj = self.strategies["IRPJ"].calculate(valor, rates["IRPJ"], presumed_percentage=Decimal("32.0"))
            csll = self.strategies["CSLL"].calculate(valor, rates["CSLL"], presumed_percentage=Decimal("32.0"))

            results.append(TaxResult(imposto="PIS", base_calculo=valor, aliquota=rates["PIS"], valor_tributo=pis, tipo="DEVIDO"))
            results.append(TaxResult(imposto="COFINS", base_calculo=valor, aliquota=rates["COFINS"], valor_tributo=cofins, tipo="DEVIDO"))
            results.append(TaxResult(imposto="ISS", base_calculo=valor, aliquota=rates["ISS"], valor_tributo=iss, tipo="DEVIDO"))
            results.append(TaxResult(imposto="IRPJ", base_calculo=valor, aliquota=rates["IRPJ"], valor_tributo=irpj, tipo="DEVIDO"))
            results.append(TaxResult(imposto="CSLL", base_calculo=valor, aliquota=rates["CSLL"], valor_tributo=csll, tipo="DEVIDO"))

        elif tipo_operacao.upper() in ["DESPESA", "SERVICO_TOMADO"]:
            # Retenções na fonte se aplicável
            if valor >= Decimal("671.00"):
                irrf = self.strategies["IRRF"].calculate(valor, rates["IRRF"])
                results.append(TaxResult(imposto="IRRF", base_calculo=valor, aliquota=rates["IRRF"], valor_tributo=irrf, tipo="RETIDO"))

        return results
