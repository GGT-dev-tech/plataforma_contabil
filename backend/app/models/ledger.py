"""
Módulo: Motor Contábil (Ledger)
Baseado no Princípio das Partidas Dobradas.
Substitui o antigo lancamento_v2.py
"""
import enum
from sqlalchemy import Column, String, Date, Numeric, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase

class StatusPeriodo(str, enum.Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"

class TipoPartida(str, enum.Enum):
    DEBITO = "D"
    CREDITO = "C"

class StatusLancamento(str, enum.Enum):
    RASCUNHO = "RASCUNHO"
    CONFIRMADO = "CONFIRMADO"
    EXPORTADO = "EXPORTADO"
    CANCELADO = "CANCELADO"

class ModuloOrigem(str, enum.Enum):
    FINANCEIRO = "FINANCEIRO"
    FISCAL = "FISCAL"
    FOLHA = "FOLHA"
    MANUAL = "MANUAL"

class PeriodoContabil(AuditableBase):
    """
    Controla o fechamento mensal da contabilidade.
    Se um período está FECHADO, o LedgerController bloqueia inserções ou edições para essa competência.
    """
    __tablename__ = 'periodos_contabeis'
    
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    ano_mes = Column(String(7), nullable=False, index=True) # Formato YYYY-MM
    status = Column(Enum(StatusPeriodo), default=StatusPeriodo.ABERTO, nullable=False)
    fechado_por = Column(String(36), ForeignKey('usuarios.id'), nullable=True)
    
    empresa = relationship("Empresa")

class LancamentoCabecalho(AuditableBase):
    """
    O Fato Gerador do lançamento. Agrupa as partidas de débito e crédito.
    """
    __tablename__ = 'lancamentos_cabecalhos'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    data_competencia = Column(Date, nullable=False, index=True)
    historico_padrao = Column(String(255), nullable=False)
    numero_lote = Column(String(100), nullable=False, index=True) # Agrupador, ex: EVT-FIN-2026-001
    modulo_origem = Column(Enum(ModuloOrigem), nullable=False)
    status = Column(Enum(StatusLancamento), default=StatusLancamento.RASCUNHO, nullable=False)
    
    # Vinculos opcionais de origem
    documento_fiscal_id = Column(UUID(as_uuid=True), ForeignKey('documentos_fiscais_v2.id'), nullable=True, index=True)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), nullable=True, index=True)

    partidas = relationship("PartidaItem", back_populates="cabecalho", cascade="all, delete-orphan")
    empresa = relationship("Empresa")

class PartidaItem(AuditableBase):
    """
    As linhas do lançamento (Débito e Crédito).
    """
    __tablename__ = 'partidas_itens'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    cabecalho_id = Column(UUID(as_uuid=True), ForeignKey('lancamentos_cabecalhos.id'), nullable=False, index=True)
    conta_contabil_id = Column(UUID(as_uuid=True), ForeignKey('plano_de_contas.id'), nullable=False, index=True)
    centro_custo_id = Column(UUID(as_uuid=True), nullable=True) # opcional para o futuro
    
    natureza = Column(Enum(TipoPartida), nullable=False) # D ou C
    valor = Column(Numeric(15, 2), nullable=False)
    historico_complementar = Column(String(255), nullable=True)

    cabecalho = relationship("LancamentoCabecalho", back_populates="partidas")
    conta_contabil = relationship("PlanoDeContas")
    empresa = relationship("Empresa")

class TemplateLancamento(AuditableBase):
    """
    Templates pré-configurados para geração automática de lançamentos.
    """
    __tablename__ = 'templates_lancamento'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)

    # Gatilho do template
    natureza_operacao = Column(String(30), nullable=True)
    tipo_documento = Column(String(20), nullable=True)
    regime_tributario = Column(String(30), nullable=True)

    partidas_json = Column(Text, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

