import enum
import uuid
from sqlalchemy import Column, String, Float, Enum, Date, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import AuditableBase

class TipoTransacao(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class ContaBancaria(AuditableBase):
    """
    Representa uma conta corrente ou caixa da Construtora.
    """
    __tablename__ = 'contas_bancarias'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    banco = Column(String(100), nullable=False)
    agencia = Column(String(20), nullable=True)
    conta = Column(String(20), nullable=True)
    descricao = Column(String(255), nullable=False)
    saldo_atual = Column(Float, default=0.0, nullable=False)

class TransacaoBancaria(AuditableBase):
    """
    Representa uma movimentação no extrato bancário.
    """
    __tablename__ = 'transacoes_bancarias'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conta_bancaria_id = Column(String(36), ForeignKey('contas_bancarias.id'), index=True, nullable=False)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    data_transacao = Column(Date, nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String(255), nullable=False)
    
    # Conciliação opcional
    titulo_financeiro_id = Column(String(36), ForeignKey('titulos_financeiros.id'), nullable=True)
