from typing import Dict, Any
from app.contexts.fiscal_engine.strategies.base import TaxStrategy
from app.models.fiscal import ApuracaoFiscal, DetalheImposto, TipoImposto

class LucroRealStrategy(TaxStrategy):
    """
    Estratégia para Lucro Real.
    - IRPJ e CSLL são baseados no Lucro Contábil (Receitas - Despesas).
    - PIS e COFINS são Não-Cumulativos (9.25% no total), permitindo abater créditos.
    """
    
    # Aliquotas Lucro Real (Regra Geral - Não Cumulativo)
    # IRPJ: 15% sobre o Lucro Contábil Ajustado (Adicional de 10% omitido no MVP)
    # CSLL: 9% sobre o Lucro Contábil Ajustado
    # PIS: 1.65% sobre Faturamento
    # COFINS: 7.6% sobre Faturamento
    # ISS: Variavel, assumindo 5% como default
    
    def apurar_impostos(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        faturamento_mes = dados_faturamento.get("faturamento_bruto", 0.0)
        
        # Diferença crucial: Lucro Real baseia-se no lucro e não apenas na receita bruta
        lucro_contabil = dados_faturamento.get("lucro_contabil", faturamento_mes * 0.10) # 10% fallback
        
        # PIS/COFINS Não Cumulativos permitem descontar créditos (ex: aluguel, energia, insumos)
        creditos_pis_cofins = dados_faturamento.get("creditos_pis_cofins", 0.0)
        
        retencoes = dados_faturamento.get("retencoes", {})
        retencao_ir = retencoes.get("irrf", 0.0)
        retencao_csll = retencoes.get("csll", 0.0)
        retencao_pis = retencoes.get("pis", 0.0)
        retencao_cofins = retencoes.get("cofins", 0.0)
        retencao_iss = retencoes.get("iss", 0.0)
        
        apuracao = ApuracaoFiscal(
            empresa_id=self.empresa.id,
            competencia=competencia,
            faturamento_total=faturamento_mes,
            imposto_devido=0.0
        )
        
        total_a_pagar = 0.0
        
        # 1. IRPJ e CSLL (Sobre o Lucro)
        irpj_apurado = lucro_contabil * 0.15
        csll_apurado = lucro_contabil * 0.09
        
        # 2. PIS e COFINS Não-Cumulativos (Sobre Faturamento)
        pis_apurado = faturamento_mes * 0.0165
        cofins_apurado = faturamento_mes * 0.076
        
        # 3. ISS
        iss_apurado = faturamento_mes * 0.05
        
        # Rateio do crédito PIS/COFINS (proporcional às alíquotas)
        # 1.65 / 9.25 = ~17.8% para PIS
        credito_pis = creditos_pis_cofins * (0.0165 / 0.0925) if creditos_pis_cofins else 0.0
        credito_cofins = creditos_pis_cofins * (0.076 / 0.0925) if creditos_pis_cofins else 0.0
        
        impostos = [
            (TipoImposto.IRPJ, 0.15, lucro_contabil, irpj_apurado, retencao_ir, 0.0),
            (TipoImposto.CSLL, 0.09, lucro_contabil, csll_apurado, retencao_csll, 0.0),
            (TipoImposto.PIS, 0.0165, faturamento_mes, pis_apurado, retencao_pis, credito_pis),
            (TipoImposto.COFINS, 0.076, faturamento_mes, cofins_apurado, retencao_cofins, credito_cofins),
            (TipoImposto.ISS, 0.05, faturamento_mes, iss_apurado, retencao_iss, 0.0),
        ]
        
        for tipo, aliquota, base, apurado, retido, credito in impostos:
            # Imposto a pagar = Apurado - Retido - Créditos Não Cumulativos
            a_pagar = max(0.0, apurado - retido - credito)
            
            detalhe = DetalheImposto(
                tipo_imposto=tipo,
                base_de_calculo=base,
                aliquota=aliquota,
                valor_apurado=apurado,
                valor_retido=retido,
                valor_a_pagar=a_pagar
            )
            apuracao.detalhes.append(detalhe)
            total_a_pagar += a_pagar
            
        apuracao.imposto_devido = total_a_pagar
        
        return apuracao
