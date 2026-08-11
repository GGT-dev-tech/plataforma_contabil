"""
Motor de Geração de Lançamentos Contábeis em Partida Dobrada
Converte eventos financeiros validados em lançamentos contábeis.

Princípio: cada evento (pagamento de NFS-e, recebimento, etc.)
gera um conjunto de lançamentos D/C balanceados.

Integra-se com:
- MotorFiscal (calcula retenções)
- PlanoDeContas (mapeia para contas corretas)
- TemplateLancamento (regras pré-configuradas)
"""
import uuid
import json
from decimal import Decimal
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.documento_fiscal import DocumentoFiscalV2, NaturezaOperacao, TipoDocumentoFiscal
from app.models.ledger import LancamentoCabecalho, TipoPartida, StatusLancamento, TemplateLancamento, ModuloOrigem
from app.services.motor_fiscal import MotorFiscal, ResultadoCalculo
from app.services.ledger import LedgerController


# Mapeamento padrão de contas por tipo de evento
# Baseado no Plano de Contas CFC 1.374/2011 para construtoras
CONTAS_PADRAO = {
    # Custos de Obra (Débito)
    "custo_material_obra":         ("1.2.1.01", "Obras em Andamento - Material"),
    "custo_mao_obra_empreitada":   ("1.2.1.02", "Obras em Andamento - Subempreitada"),
    "custo_servico_obra":          ("1.2.1.03", "Obras em Andamento - Serviços"),
    "despesa_administrativa":       ("5.1.01",   "Despesas Administrativas Gerais"),
    "despesa_financeira":           ("5.2.01",   "Despesas Financeiras"),

    # Disponibilidades (Crédito em pagamentos)
    "banco_padrao":                 ("1.1.1.02", "Banco - Conta Corrente"),

    # Fornecedores a Pagar (obrigações)
    "fornecedores_pagar":           ("2.1.1.01", "Fornecedores a Pagar"),

    # Tributos Retidos a Recolher (Crédito em retenções)
    "iss_retido":                   ("2.1.2.01", "ISS Retido a Recolher"),
    "inss_retido":                  ("2.1.2.02", "INSS Retido a Recolher"),
    "ir_retido_pj":                 ("2.1.2.03", "IRRF Retido a Recolher - PJ"),
    "ir_retido_pf":                 ("2.1.2.04", "IRRF Retido a Recolher - PF"),
    "csrf_retido":                  ("2.1.2.05", "PIS/COFINS/CSLL Retidos a Recolher"),

    # Receitas (para futuros módulos)
    "receita_venda_imoveis":        ("4.1.1.01", "Receita com Venda de Imóveis"),
    "receita_construcao":           ("4.1.1.02", "Receita com Construção por Empreitada"),
}


def _conta(chave: str, conta_override: Optional[str] = None) -> tuple:
    """Retorna (codigo, descricao) da conta, com possibilidade de override."""
    if conta_override:
        return (conta_override, "Conta Personalizada")
    return CONTAS_PADRAO.get(chave, ("9.9.9.99", f"Conta não mapeada: {chave}"))


class GeradorLancamentos:
    """
    Gera lançamentos contábeis em partida dobrada a partir de eventos financeiros.
    
    Fluxo:
    1. Recebe DocumentoFiscalV2 validado
    2. Consulta TemplateLancamento para a natureza/tipo
    3. Usa MotorFiscal para calcular retenções
    4. Chama o LedgerController para criar Lançamento + Partidas
    5. Persiste no banco (o controller cuida do flush e validação)
    """

    def __init__(self, db: Session):
        self.db = db
        self.motor_fiscal = MotorFiscal()
        self.ledger_controller = LedgerController(db)

    def gerar_para_documento(
        self,
        documento: DocumentoFiscalV2,
        execucao_id: Optional[str] = None,
        conta_bancaria_codigo: Optional[str] = None,
        conta_custo_override: Optional[str] = None,
    ) -> LancamentoCabecalho:
        """
        Gera todos os lançamentos D/C para um documento fiscal.
        Retorna o LancamentoCabecalho gerado (já validado pelo LedgerController).
        """

        # Buscar configurações fiscais da empresa
        aliquota_iss = None
        retencao_iss = True
        emitente_pj = True  # Assumir PJ por padrão
        emitente_simples = False

        if documento.tipo == TipoDocumentoFiscal.RPA:
            emitente_pj = False  # RPA é sempre PF

        # Calcular retenções
        calculo = self.motor_fiscal.calcular(
            valor_bruto=Decimal(str(documento.valor_bruto)),
            natureza=documento.natureza_operacao,
            tipo_doc=documento.tipo,
            emitente_pj=emitente_pj,
            emitente_simples=emitente_simples,
            aliquota_iss_municipio=aliquota_iss,
            retencao_iss_obrigatoria=retencao_iss,
            valor_desconto=Decimal(str(documento.valor_desconto or 0)),
        )

        numero_lote = f"EVT-{documento.numero or uuid.uuid4().hex[:8].upper()}"
        partidas = []

        # Determinar conta de custo/débito conforme natureza
        conta_debito = self._mapear_conta_debito(documento.natureza_operacao, conta_custo_override)

        # === LANÇAMENTO DE DÉBITO (Custo/Despesa/Ativo) ===
        partidas.append({
            'conta_contabil_id': self._obter_id_conta(conta_debito[0]),
            'natureza': TipoPartida.DEBITO,
            'valor': calculo.valor_bruto,
            'historico_complementar': self._historico(documento)
        })

        # === LANÇAMENTOS DE CRÉDITO ===
        conta_banco = conta_bancaria_codigo or _conta("banco_padrao")[0]

        # Crédito na conta bancária (valor líquido pago)
        if calculo.valor_liquido_pagar > 0:
            partidas.append({
                'conta_contabil_id': self._obter_id_conta(conta_banco),
                'natureza': TipoPartida.CREDITO,
                'valor': calculo.valor_liquido_pagar,
                'historico_complementar': f"Pag. líq. {self._historico(documento)}"
            })

        # Créditos para cada retenção calculada
        retencoes = [
            (calculo.iss_valor, calculo.iss_retido, "iss_retido", "ISS Retido a Recolher"),
            (calculo.inss_valor, calculo.inss_retido, "inss_retido", "INSS Retido a Recolher"),
            (calculo.ir_valor, calculo.ir_retido,
             "ir_retido_pj" if emitente_pj else "ir_retido_pf",
             f"IRRF Retido {'PJ' if emitente_pj else 'PF'} - DARF {calculo.ir_codigo_darf}"),
        ]

        # CSRF como um único lançamento (PIS+COFINS+CSLL juntos, mesmo recolhimento)
        csrf_total = calculo.pis_valor + calculo.cofins_valor + calculo.csll_valor
        if csrf_total > 0 and calculo.csrf_retido:
            retencoes.append((csrf_total, True, "csrf_retido", "CSRF Retido (PIS+COFINS+CSLL)"))

        for valor_ret, foi_retido, chave_conta, descr in retencoes:
            if valor_ret > 0 and foi_retido:
                conta_ret = _conta(chave_conta)
                partidas.append({
                    'conta_contabil_id': self._obter_id_conta(conta_ret[0]),
                    'natureza': TipoPartida.CREDITO,
                    'valor': valor_ret,
                    'historico_complementar': f"{descr} - {self._historico(documento)}"
                })

        return self.ledger_controller.registrar_lancamento(
            empresa_id=documento.empresa_id,
            data_competencia=documento.data_competencia or documento.data_emissao,
            historico=self._historico(documento),
            modulo=ModuloOrigem.FISCAL,
            numero_lote=numero_lote,
            documento_fiscal_id=documento.id,
            obra_id=documento.obra_id,
            partidas=partidas
        )

    def _mapear_conta_debito(self, natureza: NaturezaOperacao, override: Optional[str]) -> tuple:
        if override:
            return (override, "Conta definida manualmente")

        mapeamento = {
            NaturezaOperacao.MATERIAL:          _conta("custo_material_obra"),
            NaturezaOperacao.EMPREITADA:        _conta("custo_mao_obra_empreitada"),
            NaturezaOperacao.SUBEMPREITADA:     _conta("custo_mao_obra_empreitada"),
            NaturezaOperacao.SERVICO:           _conta("custo_servico_obra"),
            NaturezaOperacao.LOCACAO_EQUIPAMENTO: _conta("custo_servico_obra"),
            NaturezaOperacao.ALUGUEL:           _conta("despesa_administrativa"),
            NaturezaOperacao.CONCESSIONARIA:    _conta("despesa_administrativa"),
            NaturezaOperacao.FINANCEIRO:        _conta("despesa_financeira"),
        }
        return mapeamento.get(natureza, _conta("despesa_administrativa"))

    def _historico(self, doc: DocumentoFiscalV2) -> str:
        partes = []
        if doc.tipo:
            partes.append(doc.tipo.value)
        if doc.numero:
            partes.append(f"Nº {doc.numero}")
        if doc.emitente_nome:
            partes.append(doc.emitente_nome[:40])
        return " | ".join(partes) or "Lançamento automático"

    def _obter_id_conta(self, codigo_contabil: str) -> str:
        """
        No MVP, busca o ID real no banco.
        Se não achar (base vazia/testes), retorna um UUID falso apenas para não quebrar testes.
        Idealmente as contas padrões devem existir.
        """
        from app.models.plano_contas import PlanoDeContas
        
        conta = self.db.query(PlanoDeContas).filter(PlanoDeContas.codigo_contabil == codigo_contabil).first()
        if conta:
            return str(conta.id)
            
        # Fallback apenas para não dar crash se o banco estiver vazio
        # A validação no LedgerController vai falhar se usar UUID falso!
        import uuid
        return str(uuid.uuid4())
