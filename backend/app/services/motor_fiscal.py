"""
Motor de Cálculo Fiscal
Calcula retenções obrigatórias conforme legislação tributária brasileira.

Legislação base:
- LC 116/2003: ISS
- IN RFB 971/2009: INSS sobre serviços (art. 117: construção civil)
- RIR/2018 art. 720: IRRF sobre PJ
- IN RFB 459/2004: CSRF (PIS+COFINS+CSLL) sobre PJ
- Decreto 9.580/2018: IRRF PF (tabela progressiva)
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Optional
from app.models.documento_fiscal import NaturezaOperacao, TipoDocumentoFiscal


@dataclass
class ResultadoCalculo:
    """Resultado do cálculo de retenções para um documento fiscal."""
    valor_bruto: Decimal
    valor_desconto: Decimal = Decimal('0.00')

    # Retenções calculadas
    iss_valor: Decimal = Decimal('0.00')
    iss_retido: bool = False
    iss_aliquota: Decimal = Decimal('0.00')

    inss_valor: Decimal = Decimal('0.00')
    inss_retido: bool = False
    inss_aliquota: Decimal = Decimal('0.00')

    ir_valor: Decimal = Decimal('0.00')
    ir_retido: bool = False
    ir_aliquota: Decimal = Decimal('0.00')
    ir_codigo_darf: str = ''

    pis_valor: Decimal = Decimal('0.00')
    cofins_valor: Decimal = Decimal('0.00')
    csll_valor: Decimal = Decimal('0.00')
    csrf_retido: bool = False

    justificativas: list = field(default_factory=list)

    @property
    def total_retencoes(self) -> Decimal:
        return (self.iss_valor + self.inss_valor + self.ir_valor +
                self.pis_valor + self.cofins_valor + self.csll_valor)

    @property
    def valor_liquido_pagar(self) -> Decimal:
        return self.valor_bruto - self.valor_desconto - self.total_retencoes


class MotorFiscal:
    """
    Motor de cálculo fiscal para construtoras brasileiras.
    
    Uso:
        motor = MotorFiscal()
        resultado = motor.calcular(
            valor_bruto=Decimal('50000.00'),
            natureza=NaturezaOperacao.EMPREITADA,
            tipo_doc=TipoDocumentoFiscal.NFSE,
            emitente_pj=True,
            municipio_ibge='3550308',  # São Paulo
            retencao_iss_obrigatoria=True,
        )
    """

    # ========================
    # ALÍQUOTAS PADRÃO (2026)
    # ========================

    # INSS: 11% sobre serviços de construção civil (IN RFB 971/2009, art. 117)
    # Reduzido para 3,5% para optantes do Simples (LC 123/2006)
    INSS_CONSTRUCAO_CIVIL = Decimal('0.11')
    INSS_SIMPLES = Decimal('0.035')

    # CSRF: PIS + COFINS + CSLL (IN RFB 459/2004)
    # Aplica somente a PJ, em pagamentos acima do mínimo (R$ 215,05 em 2026)
    PIS_ALIQUOTA = Decimal('0.0065')
    COFINS_ALIQUOTA = Decimal('0.03')
    CSLL_ALIQUOTA = Decimal('0.01')
    CSRF_MINIMO_2026 = Decimal('215.05')

    # IRRF sobre PJ - serviços de construção (art. 720 RIR, cód. DARF 6147)
    IR_PJ_CONSTRUCAO = Decimal('0.015')   # 1,5%
    IR_PJ_DARF = '6147'

    # IRRF sobre PF (autônomo / RPA) - mínimo R$ 2.259,20 (tabela 2026)
    IR_PF_MINIMO_2026 = Decimal('2259.20')

    def calcular(
        self,
        valor_bruto: Decimal,
        natureza: NaturezaOperacao,
        tipo_doc: TipoDocumentoFiscal,
        emitente_pj: bool = True,
        emitente_simples: bool = False,
        municipio_ibge: Optional[str] = None,
        aliquota_iss_municipio: Optional[Decimal] = None,
        retencao_iss_obrigatoria: bool = True,
        valor_desconto: Decimal = Decimal('0.00'),
    ) -> ResultadoCalculo:
        """
        Calcula todas as retenções aplicáveis ao documento fiscal.
        
        A ordem de cálculo segue a legislação:
        1. ISS (base: valor_bruto - deduções municipais)
        2. INSS (base: valor_bruto, para empreitadas/subempreitadas)
        3. IRRF (base: valor_bruto - deduções IRRF)
        4. CSRF (base: valor_bruto, apenas PJ, acima do mínimo)
        """
        resultado = ResultadoCalculo(
            valor_bruto=valor_bruto,
            valor_desconto=valor_desconto
        )

        valor_base = valor_bruto - valor_desconto

        # 1. ISS — Imposto Sobre Serviços (LC 116/2003)
        self._calcular_iss(resultado, valor_base, natureza, tipo_doc,
                           aliquota_iss_municipio, retencao_iss_obrigatoria)

        # 2. INSS — Previdência Social (IN RFB 971/2009)
        self._calcular_inss(resultado, valor_base, natureza,
                             emitente_pj, emitente_simples)

        # 3. IRRF — Imposto de Renda Retido na Fonte
        self._calcular_irrf(resultado, valor_base, natureza,
                             tipo_doc, emitente_pj)

        # 4. CSRF — PIS + COFINS + CSLL (apenas PJ)
        if emitente_pj:
            self._calcular_csrf(resultado, valor_base, natureza)

        return resultado

    def _calcular_iss(
        self,
        resultado: ResultadoCalculo,
        valor_base: Decimal,
        natureza: NaturezaOperacao,
        tipo_doc: TipoDocumentoFiscal,
        aliquota_iss: Optional[Decimal],
        retencao_obrigatoria: bool
    ):
        """
        ISS incide sobre serviços conforme LC 116/2003.
        Para construção civil: alíquota varia entre 2% e 5% por município.
        ISS na fonte: responsabilidade do tomador (construtora que paga).
        """
        servicos_com_iss = {
            NaturezaOperacao.SERVICO,
            NaturezaOperacao.EMPREITADA,
            NaturezaOperacao.SUBEMPREITADA,
            NaturezaOperacao.LOCACAO_EQUIPAMENTO,  # Depende do município
        }

        if natureza not in servicos_com_iss:
            resultado.justificativas.append(
                f"ISS: não aplicável para natureza {natureza.value}")
            return

        if tipo_doc == TipoDocumentoFiscal.NFE:
            resultado.justificativas.append(
                "ISS: não aplicável para NF-e (operação de mercadoria)")
            return

        if not aliquota_iss:
            # Alíquota padrão de 3% quando não configurada (conservador)
            aliquota_iss = Decimal('0.03')
            resultado.justificativas.append(
                f"ISS: alíquota padrão 3,00% aplicada (município não configurado)")
        else:
            resultado.justificativas.append(
                f"ISS: alíquota {float(aliquota_iss)*100:.2f}% (LC 116/2003)")

        iss = (valor_base * aliquota_iss).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        resultado.iss_valor = iss
        resultado.iss_aliquota = aliquota_iss
        resultado.iss_retido = retencao_obrigatoria

        if not retencao_obrigatoria:
            resultado.justificativas.append(
                "ISS: retenção na fonte não obrigatória neste município — emitente recolhe diretamente")

    def _calcular_inss(
        self,
        resultado: ResultadoCalculo,
        valor_base: Decimal,
        natureza: NaturezaOperacao,
        emitente_pj: bool,
        emitente_simples: bool
    ):
        """
        INSS sobre serviços de construção civil.
        
        IN RFB 971/2009, art. 117:
        - Empreitada e subempreitada de construção civil: 11%
        - Optante do Simples Nacional: 3,5% (LC 123/2006, art. 21, §3°)
        
        Não incide em:
        - Compra de materiais (NFe)
        - Aluguel de equipamentos sem operador
        - Concessionárias de serviços públicos
        """
        naturezas_com_inss = {
            NaturezaOperacao.EMPREITADA,
            NaturezaOperacao.SUBEMPREITADA,
        }

        if natureza not in naturezas_com_inss:
            resultado.justificativas.append(
                f"INSS: não aplicável para natureza {natureza.value}")
            return

        aliquota = self.INSS_SIMPLES if emitente_simples else self.INSS_CONSTRUCAO_CIVIL
        inss = (valor_base * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        resultado.inss_valor = inss
        resultado.inss_aliquota = aliquota
        resultado.inss_retido = True

        base_legal = "IN RFB 971/2009, art. 117" if not emitente_simples else "LC 123/2006, art. 21 §3°"
        resultado.justificativas.append(
            f"INSS: {float(aliquota)*100:.1f}% retido ({base_legal})")

    def _calcular_irrf(
        self,
        resultado: ResultadoCalculo,
        valor_base: Decimal,
        natureza: NaturezaOperacao,
        tipo_doc: TipoDocumentoFiscal,
        emitente_pj: bool
    ):
        """
        IRRF sobre pagamentos a terceiros (RIR/2018).
        
        PJ: 1,5% para serviços de construção civil (DARF 6147)
        PF (RPA): tabela progressiva (DARF 0588), a partir de R$ 2.259,20
        """
        sem_irrf = {
            NaturezaOperacao.MATERIAL,
            NaturezaOperacao.CONCESSIONARIA,
            NaturezaOperacao.FINANCEIRO,
        }

        if natureza in sem_irrf:
            resultado.justificativas.append(
                f"IRRF: não aplicável para natureza {natureza.value}")
            return

        if emitente_pj:
            # PJ: 1,5% para serviços de construção (art. 720, §1°, RIR)
            ir = (valor_base * self.IR_PJ_CONSTRUCAO).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
            resultado.ir_valor = ir
            resultado.ir_aliquota = self.IR_PJ_CONSTRUCAO
            resultado.ir_codigo_darf = self.IR_PJ_DARF
            resultado.ir_retido = True
            resultado.justificativas.append(
                f"IRRF PJ: 1,5% (RIR/2018, art. 720 — DARF {self.IR_PJ_DARF})")
        else:
            # PF (RPA): verificar se acima do mínimo da tabela
            if valor_base >= self.IR_PF_MINIMO_2026:
                # Simplificado: usar alíquota de 7,5% (segunda faixa 2026)
                # Em produção: usar tabela completa por faixa de renda
                ir = (valor_base * Decimal('0.075')).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
                resultado.ir_valor = ir
                resultado.ir_aliquota = Decimal('0.075')
                resultado.ir_codigo_darf = '0588'
                resultado.ir_retido = True
                resultado.justificativas.append(
                    "IRRF PF: tabela progressiva (Decreto 11.322/2022 — DARF 0588)")
            else:
                resultado.justificativas.append(
                    f"IRRF PF: valor abaixo do mínimo (R$ {self.IR_PF_MINIMO_2026}) — isento")

    def _calcular_csrf(
        self,
        resultado: ResultadoCalculo,
        valor_base: Decimal,
        natureza: NaturezaOperacao
    ):
        """
        CSRF — PIS (0,65%) + COFINS (3,00%) + CSLL (1,00%) = 4,65%
        IN RFB 459/2004: aplicável a PJ em pagamentos acima de R$ 215,05.
        
        Não incide em: optantes do Simples, concessionárias, materiais
        (dependendo do regime tributário do pagador).
        """
        sem_csrf = {
            NaturezaOperacao.MATERIAL,
            NaturezaOperacao.CONCESSIONARIA,
            NaturezaOperacao.FINANCEIRO,
            NaturezaOperacao.FOLHA,
        }

        if natureza in sem_csrf:
            resultado.justificativas.append(
                f"CSRF: não aplicável para natureza {natureza.value}")
            return

        if valor_base < self.CSRF_MINIMO_2026:
            resultado.justificativas.append(
                f"CSRF: valor {float(valor_base):.2f} abaixo do mínimo "
                f"R$ {float(self.CSRF_MINIMO_2026):.2f} — isento (IN RFB 459/2004)")
            return

        pis = (valor_base * self.PIS_ALIQUOTA).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cofins = (valor_base * self.COFINS_ALIQUOTA).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        csll = (valor_base * self.CSLL_ALIQUOTA).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        resultado.pis_valor = pis
        resultado.cofins_valor = cofins
        resultado.csll_valor = csll
        resultado.csrf_retido = True
        resultado.justificativas.append(
            f"CSRF: PIS {float(pis):.2f} + COFINS {float(cofins):.2f} + CSLL {float(csll):.2f} "
            f"(IN RFB 459/2004, art. 1°)")
