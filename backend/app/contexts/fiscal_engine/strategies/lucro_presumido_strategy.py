from typing import Dict, Any, List
from app.contexts.fiscal_engine.strategies.base import TaxStrategy
from app.models.fiscal import ApuracaoFiscal, DetalheImposto, TipoImposto

class LucroPresumidoStrategy(TaxStrategy):
    """
    Estratégia para Lucro Presumido.
    Calcula PIS, COFINS, IRPJ, CSLL e ISS.
    Neste exemplo, assumimos faturamento mensal para fins de simplificação (embora IRPJ/CSLL sejam trimestrais).
    Também abate retenções informadas.
    """
    
    # Aliquotas padrao Lucro Presumido (Serviços Gerais - Presunção 32%)
    # IRPJ: 15% sobre a base (32%) = 4.8% efetiva (desconsiderando adicional IR)
    # CSLL: 9% sobre a base (32%) = 2.88% efetiva
    # PIS: 0.65%
    # COFINS: 3.00%
    # ISS: Variavel, assumindo 5% como default
    
    def apurar_impostos(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        faturamento_mes = dados_faturamento.get("faturamento_bruto", 0.0)
        retencoes = dados_faturamento.get("retencoes", {})
        
        retencao_ir = retencoes.get("irrf", 0.0)
        retencao_csll = retencoes.get("csll", 0.0)
        retencao_pis = retencoes.get("pis", 0.0)
        retencao_cofins = retencoes.get("cofins", 0.0)
        retencao_iss = retencoes.get("iss", 0.0)
        
        # Base de Calculo = Faturamento
        # A aliquota aqui eh a efetiva direta sobre a receita bruta (base de presuncao ja embutida)
        impostos = [
            (TipoImposto.IRPJ, 0.048, retencao_ir),
            (TipoImposto.CSLL, 0.0288, retencao_csll),
            (TipoImposto.PIS, 0.0065, retencao_pis),
            (TipoImposto.COFINS, 0.03, retencao_cofins),
            (TipoImposto.ISS, 0.05, retencao_iss),
        ]
        
        apuracao = ApuracaoFiscal(
            empresa_id=self.empresa.id,
            competencia=competencia,
            faturamento_total=faturamento_mes,
            imposto_devido=0.0
        )
        
        total_a_pagar = 0.0
        
        for tipo, aliquota, retido in impostos:
            apurado = faturamento_mes * aliquota
            # Imposto a pagar = Apurado - Retido
            # Se for negativo, fica saldo credor (0.0 a pagar)
            a_pagar = max(0.0, apurado - retido)
            
            detalhe = DetalheImposto(
                tipo_imposto=tipo,
                base_de_calculo=faturamento_mes,
                aliquota=aliquota,
                valor_apurado=apurado,
                valor_retido=retido,
                valor_a_pagar=a_pagar
            )
            apuracao.detalhes.append(detalhe)
            total_a_pagar += a_pagar
            
        apuracao.imposto_devido = total_a_pagar
        
        return apuracao
