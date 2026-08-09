"""
Módulo: Documento Fiscal
Entidade central do sistema — substitui o conceito simplificado de 'Despesa'.

No Brasil, toda operação financeira de uma empresa é lastreada por um documento fiscal:
- NF-e (Nota Fiscal Eletrônica)     → mercadorias/materiais (SEFAZ)
- NFS-e (Nota Fiscal de Serviços)   → serviços (prefeituras)
- CT-e (Conhecimento de Transporte) → fretes
- RPA (Recibo de Pagamento Autônomo)→ pessoa física sem NF
- Fatura / Contrato                  → empreitadas mensais
- Recibo                             → situações excepcionais

Impostos retidos na fonte (responsabilidade do tomador):
- ISS: 2% a 5% conforme município (LC 116/2003)
- INSS: 11% sobre serviços de construção (IN RFB 971/2009, art. 117)
- IRRF: 1,5% a 15% conforme natureza (RIR/2018, art. 720)
- PIS/COFINS/CSLL: 4,65% em pagamentos a PJ acima de R$ 215,05 (IN RFB 459/2004)
"""
from sqlalchemy import Column, String, Date, Numeric, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase
import enum


class TipoDocumentoFiscal(str, enum.Enum):
    NFE = "NFE"              # Nota Fiscal Eletrônica (materiais, CFOP, NCM)
    NFSE = "NFSE"            # Nota Fiscal de Serviço Eletrônica (prefeitura)
    CTE = "CTE"              # Conhecimento de Transporte Eletrônico
    RPA = "RPA"              # Recibo de Pagamento a Autônomo (PF sem CNPJ)
    FATURA = "FATURA"        # Fatura de empreitada ou contrato
    RECIBO = "RECIBO"        # Recibo simples
    BOLETO = "BOLETO"        # Boleto bancário sem NF associada (aluguel, condomínio)


class NaturezaOperacao(str, enum.Enum):
    """
    Natureza da operação define o tratamento fiscal aplicável.
    Crítica para calcular corretamente as retenções.
    """
    MATERIAL = "MATERIAL"                    # Compra de material (NF-e CFOP 1.102/2.102)
    SERVICO = "SERVICO"                      # Serviço prestado (NFS-e genérico)
    EMPREITADA = "EMPREITADA"                # Empreitada de obra (INSS 11% + ISS + IRRF)
    SUBEMPREITADA = "SUBEMPREITADA"          # Sub-empreitada de mão de obra (INSS 11%)
    LOCACAO_EQUIPAMENTO = "LOCACAO_EQUIPAMENTO"  # Sem ISS, com IRRF se PJ
    ALUGUEL = "ALUGUEL"                      # Aluguel de imóvel (IRRF 7,5%~27,5% PF)
    CONCESSIONARIA = "CONCESSIONARIA"        # Energia, água, telefone (sem retenção)
    FINANCEIRO = "FINANCEIRO"                # Tarifas bancárias, IOF
    FOLHA = "FOLHA"                          # Pagamento de salários (INSS + IRRF + FGTS)


class StatusDocumentoFiscal(str, enum.Enum):
    PENDENTE = "PENDENTE"            # Documento recebido, aguarda aprovação
    APROVADO = "APROVADO"            # Documento validado e aprovado para pagamento
    PAGO = "PAGO"                    # Pagamento concluído e conciliado
    CANCELADO = "CANCELADO"          # NF cancelada na SEFAZ/Prefeitura
    REJEITADO = "REJEITADO"          # Documento com inconsistência fiscal
    AGUARDANDO_NF = "AGUARDANDO_NF"  # Serviço executado, aguarda emissão de NF


class DocumentoFiscalV2(AuditableBase):
    """
    Entidade central de toda operação financeira com terceiros.
    
    Tratamento de impostos seguindo:
    - LC 116/2003 (ISS)
    - IN RFB 971/2009 (INSS sobre serviços)
    - RIR/2018 (IRRF)
    - IN RFB 459/2004 (CSRF: PIS/COFINS/CSLL)
    - IN RFB 1.234/2012 (retenções em pagamentos da Administração Pública)
    """
    __tablename__ = 'documentos_fiscais_v2'

    # Vínculos
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), nullable=True, index=True)
    fornecedor_id = Column(UUID(as_uuid=True), ForeignKey('fornecedores.id'), nullable=True, index=True)
    execucao_id = Column(String(36), ForeignKey('execucoes_pipeline.id'), nullable=True)

    # Tipo e Natureza
    tipo = Column(Enum(TipoDocumentoFiscal), nullable=False)
    natureza_operacao = Column(Enum(NaturezaOperacao), nullable=False)
    status = Column(Enum(StatusDocumentoFiscal), default=StatusDocumentoFiscal.PENDENTE, nullable=False)

    # Identificação do Documento
    numero = Column(String(20), nullable=True, index=True)
    serie = Column(String(5), nullable=True)
    chave_acesso = Column(String(44), nullable=True, unique=True, index=True)  # NF-e: 44 dígitos
    codigo_verificacao = Column(String(20), nullable=True)  # NFS-e: código verificador

    # Datas
    data_emissao = Column(Date, nullable=False)
    data_entrada = Column(Date, nullable=True)   # Data de recebimento do documento
    data_competencia = Column(Date, nullable=True)  # Competência do serviço (pode diferir da emissão)

    # Emitente (Fornecedor)
    emitente_cnpj_cpf = Column(String(20), nullable=True, index=True)
    emitente_nome = Column(String(255), nullable=True)
    emitente_municipio_ibge = Column(String(7), nullable=True)
    emitente_municipio_nome = Column(String(100), nullable=True)
    emitente_inscricao_municipal = Column(String(30), nullable=True)

    # Valores Principais
    valor_bruto = Column(Numeric(15, 2), nullable=False)
    valor_desconto = Column(Numeric(15, 2), default=0, nullable=False)
    valor_outras_deducoes = Column(Numeric(15, 2), default=0, nullable=False)
    valor_base_calculo = Column(Numeric(15, 2), nullable=True)  # Base para ISS/IR

    # ========================
    # IMPOSTOS RETIDOS NA FONTE
    # ========================

    # ISS — Imposto Sobre Serviços (LC 116/2003, Municipal)
    iss_aliquota = Column(Numeric(5, 4), nullable=True)      # Ex: 0.0500 = 5%
    iss_valor = Column(Numeric(15, 2), default=0, nullable=False)
    iss_retido_fonte = Column(Boolean, default=False, nullable=False)
    iss_municipio_recolhimento = Column(String(7), nullable=True)  # Código IBGE

    # INSS — Previdência Social (IN RFB 971/2009)
    # Para empreitadas e subempreitadas de construção: 11%
    inss_aliquota = Column(Numeric(5, 4), nullable=True)
    inss_valor = Column(Numeric(15, 2), default=0, nullable=False)
    inss_retido = Column(Boolean, default=False, nullable=False)
    inss_artigo_retencao = Column(String(50), nullable=True)   # Art. 117, 118 da IN 971

    # IRRF — Imposto de Renda Retido na Fonte (RIR/2018)
    ir_aliquota = Column(Numeric(5, 4), nullable=True)
    ir_valor = Column(Numeric(15, 2), default=0, nullable=False)
    ir_retido = Column(Boolean, default=False, nullable=False)
    ir_codigo_darf = Column(String(10), nullable=True)  # Código DARF do IR retido

    # CSRF — PIS + COFINS + CSLL (IN RFB 459/2004)
    # Aplica-se a PJ em pagamentos acima de R$ 215,05 (valor 2026)
    pis_valor = Column(Numeric(15, 2), default=0, nullable=False)
    cofins_valor = Column(Numeric(15, 2), default=0, nullable=False)
    csll_valor = Column(Numeric(15, 2), default=0, nullable=False)
    csrf_retido = Column(Boolean, default=False, nullable=False)

    # Valor Total das Retenções
    total_retencoes = Column(Numeric(15, 2), default=0, nullable=False)

    # Valor Líquido Efetivamente Pago (valor_bruto - descontos - retenções)
    valor_liquido_pagar = Column(Numeric(15, 2), nullable=True)

    # Classificação Fiscal (NF-e específico)
    cfop = Column(String(5), nullable=True)    # Código Fiscal de Operações e Prestações
    ncm = Column(String(10), nullable=True)    # Nomenclatura Comum do Mercosul

    # Dados da NFS-e (serviços)
    codigo_servico_lc116 = Column(String(10), nullable=True)  # Item da Lista LC 116/2003
    discriminacao_servicos = Column(Text, nullable=True)

    # Controle de Importação
    importado_via = Column(String(50), nullable=True)  # XML_NFE, XML_NFSE, PLANILHA, API_ERP
    xml_original = Column(Text, nullable=True)  # XML completo do documento (para reprocessamento)
    observacoes_fiscais = Column(Text, nullable=True)

    # Relacionamentos
    empresa = relationship("Empresa")
    obra = relationship("Obra", back_populates="documentos_fiscais")
    fornecedor = relationship("Fornecedor")
    parcelas = relationship("ParcelaDocumentoFiscal", back_populates="documento", cascade="all, delete-orphan")
    lancamentos = relationship("LancamentoContabilV2", back_populates="documento_fiscal")


class ParcelaDocumentoFiscal(AuditableBase):
    """
    Parcelas de pagamento vinculadas a um documento fiscal.
    Substitui ParcelaDespesa com semântica fiscal correta.
    
    Mantém relação com o sistema de matching (conciliação bancária)
    através de ConciliacaoItem.
    """
    __tablename__ = 'parcelas_documento_fiscal'

    documento_id = Column(UUID(as_uuid=True), ForeignKey('documentos_fiscais_v2.id'), nullable=False, index=True)

    numero_parcela = Column(String(10), nullable=False, default='1/1')
    valor_parcela = Column(Numeric(15, 2), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)

    # Status específico
    status = Column(String(30), default='A_VENCER', nullable=False)
    # A_VENCER, VENCIDO, PAGO, PARCIALMENTE_PAGO, NEGOCIADO, CANCELADO

    # Forma de pagamento prevista
    forma_pagamento = Column(String(30), nullable=True)  # PIX, BOLETO, TED, DINHEIRO

    # Vinculação com movimentação bancária (resultado da conciliação)
    movimentacao_bancaria_id = Column(UUID(as_uuid=True), ForeignKey('movimentacoes_bancarias.id'), nullable=True)

    # ID de origem no ERP (para idempotência)
    id_externo_erp = Column(String(100), nullable=True, index=True)

    documento = relationship("DocumentoFiscalV2", back_populates="parcelas")
    movimentacao = relationship("MovimentacaoBancaria")
