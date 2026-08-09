"""
Módulo: Lançamento Contábil em Partida Dobrada
Expande o LancamentoContabil original para suportar partida dobrada completa.

Em contabilidade brasileira (NBC TG 1000 e ITG 2000):
- Todo lançamento tem pelo menos um débito e um crédito de mesmo valor
- Lançamentos simples: 1D × 1C
- Lançamentos compostos: 1D × NC ou ND × 1C
- Todo lançamento referencia o Plano de Contas (código contábil)

Exemplos para construção civil:
--------------------------------------------------
PAGAMENTO DE NFS-E (empreitada R$ 50.000, ISS 5% retido, INSS 11% retido):
  D 5.1.01 Custo Mão de Obra Sub-empreitada    50.000,00
  C 1.1.1.02 Banco Inter C/C                  37.500,00
  C 2.1.2.01 ISS Retido a Recolher             2.500,00
  C 2.1.2.02 INSS Retido a Recolher            5.500,00
  C 2.1.2.03 IR Retido a Recolher              4.500,00
--------------------------------------------------
COMPRA NF-E MATERIAL (R$ 132.500):
  D 1.2.1.01 Obras em Andamento - Material    132.500,00
  C 2.1.1.01 Fornecedores a Pagar            132.500,00
--------------------------------------------------
LIQUIDAÇÃO (saída bancária bate extrato):
  D 2.1.1.01 Fornecedores a Pagar            132.500,00
  C 1.1.1.02 Banco Inter C/C                 132.500,00
"""
from sqlalchemy import Column, String, Date, Numeric, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase
import enum


class TipoPartida(str, enum.Enum):
    DEBITO = "D"
    CREDITO = "C"


class StatusLancamento(str, enum.Enum):
    RASCUNHO = "RASCUNHO"        # Gerado automaticamente, aguarda revisão
    CONFIRMADO = "CONFIRMADO"    # Aprovado pelo contador
    EXPORTADO = "EXPORTADO"      # Enviado ao sistema contábil de destino
    CANCELADO = "CANCELADO"      # Estornado


class LancamentoContabilV2(AuditableBase):
    """
    Lançamento contábil em partida dobrada.
    Versão 2 — compatível com geração automática e exportação SPED ECD.
    
    Um "evento" (ex: pagamento de NFS-e) gera múltiplos lançamentos:
    - 1 lançamento de débito (custo/despesa/ativo)
    - N lançamentos de crédito (banco + tributos retidos)
    
    Todos compartilham o mesmo numero_lote (agrupador do evento).
    """
    __tablename__ = 'lancamentos_contabeis_v2'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    execucao_id = Column(String(36), ForeignKey('execucoes_pipeline.id'), nullable=True)

    # Vínculo com o Documento Fiscal que originou o lançamento
    documento_fiscal_id = Column(UUID(as_uuid=True), ForeignKey('documentos_fiscais_v2.id'), nullable=True, index=True)

    # Vínculo com a Obra (centro de custo)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), nullable=True, index=True)

    # Vínculo com a Conciliação (resultado do matching)
    conciliacao_id = Column(String(36), ForeignKey('conciliacoes.id'), nullable=True)

    # Agrupador do evento contábil (todos os lançamentos de um mesmo evento têm o mesmo lote)
    numero_lote = Column(String(50), nullable=False, index=True)  # Ex: EVT-2026-0001

    # Conta Contábil
    conta_contabil_codigo = Column(String(30), nullable=False, index=True)  # Ex: 1.1.1.02
    conta_contabil_descricao = Column(String(255), nullable=True)

    # Partida Dobrada
    partida = Column(Enum(TipoPartida), nullable=False)  # D ou C
    valor = Column(Numeric(15, 2), nullable=False)

    # Data e Identificação
    data_lancamento = Column(Date, nullable=False, index=True)
    data_competencia = Column(Date, nullable=True)  # Pode diferir da data do lançamento
    historico = Column(String(255), nullable=False)  # Descrição obrigatória pela ITG 2000

    # Controle de Status
    status = Column(Enum(StatusLancamento), default=StatusLancamento.RASCUNHO, nullable=False)

    # Sequência dentro do lote (para reconstituição da partida dobrada)
    sequencia_no_lote = Column(Integer, nullable=False, default=1)

    # Exportação SPED ECD
    numero_sequencial_diario = Column(String(20), nullable=True)  # Núm. no livro diário
    exportado_em = Column(String(30), nullable=True)  # Timestamp da exportação
    exportado_para = Column(String(50), nullable=True)  # dominio, alterdata, sped_ecd

    # Gerado automaticamente vs. digitado pelo contador
    gerado_automaticamente = Column(Boolean, default=True, nullable=False)
    revisado_por = Column(String(36), ForeignKey('usuarios.id'), nullable=True)
    revisado_em = Column(String(30), nullable=True)

    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    empresa = relationship("Empresa")
    obra = relationship("Obra")
    documento_fiscal = relationship("DocumentoFiscal", back_populates="lancamentos")
    conciliacao = relationship("Conciliacao")


# ============================================================
# TEMPLATE DE LANÇAMENTO (Regra de Negócio Contábil)
# ============================================================

class TemplateLancamento(AuditableBase):
    """
    Templates pré-configurados para geração automática de lançamentos.
    
    Cada combinação (NaturezaOperacao + TipoDocumento) tem uma sequência
    pré-definida de partidas contábeis.
    
    Ex: Pagamento NFS-e de empreitada com ISS e INSS:
    - DÉBITO:  conta_custo_obra (configurável)
    - CRÉDITO: conta_banco (da conta bancária utilizada)
    - CRÉDITO: conta_iss_retido (2.1.2.01)
    - CRÉDITO: conta_inss_retido (2.1.2.02)
    """
    __tablename__ = 'templates_lancamento'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True)  # NULL = padrão global
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)

    # Gatilho do template
    natureza_operacao = Column(String(30), nullable=True)  # NaturezaOperacao enum value
    tipo_documento = Column(String(20), nullable=True)      # TipoDocumentoFiscal enum value
    regime_tributario = Column(String(30), nullable=True)   # RegimeTributario enum value

    # Partidas (JSON serializado: lista de {partida: D/C, conta: codigo, descricao, percentual_valor})
    partidas_json = Column(Text, nullable=False)

    ativo = Column(Boolean, default=True, nullable=False)
