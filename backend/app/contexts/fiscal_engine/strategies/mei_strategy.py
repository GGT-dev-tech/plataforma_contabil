from typing import Dict, Any
from app.contexts.fiscal_engine.strategies.base import TaxStrategy
from app.models.fiscal import ApuracaoFiscal, DetalheImposto, TipoImposto

class MeiStrategy(TaxStrategy):
    """
    Estratégia para Microempreendedor Individual (MEI).
    O cálculo é fixo, baseado no salário mínimo atual.
    Neste exemplo MVP, estamos chumbando o valor de ~R$ 75 para serviços (INSS + ISS).
    """
    
    def apurar_impostos(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        faturamento_mensal = dados_faturamento.get("faturamento_bruto", 0.0)
        
        # O MEI tem imposto fixo independente do faturamento (até o teto).
        # Para Serviços: INSS (5% do mínimo) + ISS (R$ 5)
        # Vamos assumir valor fixo de R$ 75.60 para fins didáticos no MVP.
        valor_das_mei = 75.60
        
        apuracao = ApuracaoFiscal(
            empresa_id=self.empresa.id,
            competencia=competencia,
            faturamento_total=faturamento_mensal,
            imposto_devido=valor_das_mei
        )
        
        detalhe = DetalheImposto(
            tipo_imposto=TipoImposto.MEI_DAS,
            base_de_calculo=0.0, # Nao se aplica proporção
            aliquota=0.0,
            valor_apurado=valor_das_mei,
            valor_a_pagar=valor_das_mei
        )
        
        apuracao.detalhes.append(detalhe)
        
        return apuracao
