import enum
import uuid
from sqlalchemy import Column, String, Float, Enum, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase

class TipoTitulo(str, enum.Enum):
    PAGAR = "PAGAR"
    RECEBER = "RECEBER"

class StatusTitulo(str, enum.Enum):
    ABERTO = "ABERTO"
    VENCIDO = "VENCIDO"
    PARCIAL = "PARCIAL"
    LIQUIDADO = "LIQUIDADO"
    CANCELADO = "CANCELADO"

class TituloFinanceiro(AuditableBase):
    """
    Representa um Título a Pagar ou a Receber.
    Pode estar vinculado a um Documento Fiscal importado ou ser manual.
    """
    __tablename__ = 'titulos_financeiros'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), index=True, nullable=True)
    documento_fiscal_id = Column(UUID(as_uuid=True), ForeignKey('documentos_fiscais_v2.id'), nullable=True)
    
    tipo = Column(Enum(TipoTitulo), nullable=False)
    status = Column(Enum(StatusTitulo), default=StatusTitulo.ABERTO, nullable=False)
    
    descricao = Column(String(255), nullable=False)
    fornecedor_cliente_nome = Column(String(255), nullable=True)
    fornecedor_cliente_cnpj_cpf = Column(String(20), nullable=True)
    
    valor_nominal = Column(Float, nullable=False)
    valor_pago = Column(Float, default=0.0)
    
    data_emissao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    
    # Campo para automação: Se o título foi gerado automaticamente pela plataforma a partir de uma NF
    gerado_automaticamente = Column(Boolean, default=False)
    
    categoria = Column(String(100), nullable=True)
    
class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class MovimentacaoFinanceira(AuditableBase):
    """
    Representa uma linha do extrato bancário (OFX / Open Finance).
    """
    __tablename__ = 'movimentacoes_financeiras'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    data_transacao = Column(Date, nullable=False)
    valor = Column(Float, nullable=False)
    descricao_extrato = Column(String(255), nullable=False)
    documento_banco = Column(String(100), nullable=True) # Num. Documento ou Hash
    
    # Se true, essa movimentação já foi 100% amarrada a um título
    conciliada = Column(Boolean, default=False)
    
    categoria = Column(String(100), nullable=True)
    
class ConciliacaoFinanceira(AuditableBase):
    """
    Tabela de junção. "Match" entre Título e Movimentação Bancária.
    Pode ser Match Exato ou Parcial.
    """
    __tablename__ = 'conciliacoes_financeiras'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    titulo_id = Column(String(36), ForeignKey('titulos_financeiros.id'), nullable=False)
    movimentacao_id = Column(String(36), ForeignKey('movimentacoes_financeiras.id'), nullable=False)
    
    valor_conciliado = Column(Float, nullable=False) # Valor abatido do titulo
    data_conciliacao = Column(Date, nullable=False)
    
    # True se o algoritmo achou sozinho, False se o contador forçou o match manual
    match_automatico = Column(Boolean, default=True)
    confianca_match = Column(Float, nullable=True) # 0.0 a 1.0
