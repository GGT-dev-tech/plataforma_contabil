from typing import Dict, Any, List
from app.contexts.fiscal_engine.strategies.base import TaxStrategy
from app.models.fiscal import ApuracaoFiscal, DetalheImposto, TipoImposto

class SimplesNacionalStrategy(TaxStrategy):
    """
    Estratégia para Simples Nacional.
    Lida com o cálculo complexo da Receita Bruta Acumulada 12m (RBT12), 
    Fator R e Alíquota Efetiva.
    """
    
    # Dicionário de Faixas do Anexo III (Serviços gerais) - Exemplo 2026
    # Faixa: (Ate_RBT12, Aliquota_Nominal, Parcela_Deduzir)
    ANEXO_III = [
        (180000.00, 0.06, 0.00),
        (360000.00, 0.112, 9360.00),
        (720000.00, 0.135, 17640.00),
        (1800000.00, 0.16, 35640.00),
        (3600000.00, 0.21, 125640.00),
        (4800000.00, 0.33, 648000.00)
    ]
    
    # Dicionário de Faixas do Anexo V (Serviços sem Fator R ou Fator R < 28%)
    ANEXO_V = [
        (180000.00, 0.155, 0.00),
        (360000.00, 0.18, 4500.00),
        (720000.00, 0.195, 9900.00),
        (1800000.00, 0.205, 17100.00),
        (3600000.00, 0.23, 62100.00),
        (4800000.00, 0.305, 540000.00)
    ]
    
    def apurar_impostos(self, competencia: str, dados_faturamento: Dict[str, Any]) -> ApuracaoFiscal:
        faturamento_mes = dados_faturamento.get("faturamento_bruto", 0.0)
        rbt12 = dados_faturamento.get("rbt12", 0.0)
        folha_12m = dados_faturamento.get("folha_salarios_12m", 0.0)
        sujeito_fator_r = dados_faturamento.get("sujeito_fator_r", True)
        
        # 1. Avalia Fator R (se aplicável)
        usa_anexo_iii = True
        if sujeito_fator_r:
            fator_r = (folha_12m / rbt12) if rbt12 > 0 else 0
            if fator_r < 0.28:
                usa_anexo_iii = False # Cai na malha fina do Anexo V
                
        # 2. Busca a faixa e calcula a Aliquota Efetiva
        tabela = self.ANEXO_III if usa_anexo_iii else self.ANEXO_V
        aliquota_nominal = 0.0
        parcela_deduzir = 0.0
        
        for faixa_teto, aliq, parcela in tabela:
            if rbt12 <= faixa_teto:
                aliquota_nominal = aliq
                parcela_deduzir = parcela
                break
        else:
            # Se rbt12 for maior que o último teto, pega a última faixa
            aliquota_nominal = tabela[-1][1]
            parcela_deduzir = tabela[-1][2]
            
        # Alíquota Efetiva = ((RBT12 * Aliquota_Nominal) - Parcela_Deduzir) / RBT12
        if rbt12 > 0:
            aliquota_efetiva = ((rbt12 * aliquota_nominal) - parcela_deduzir) / rbt12
        else:
            # Empresa de início de atividade
            aliquota_efetiva = aliquota_nominal
            
        # Imposto devido no mês
        imposto_devido = faturamento_mes * aliquota_efetiva
        
        apuracao = ApuracaoFiscal(
            empresa_id=self.empresa.id,
            competencia=competencia,
            faturamento_total=faturamento_mes,
            imposto_devido=imposto_devido
        )
        
        detalhe = DetalheImposto(
            tipo_imposto=TipoImposto.SIMPLES_NACIONAL,
            base_de_calculo=faturamento_mes,
            aliquota=aliquota_efetiva,
            valor_apurado=imposto_devido,
            valor_a_pagar=imposto_devido
        )
        apuracao.detalhes.append(detalhe)
        
        return apuracao
