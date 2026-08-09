import enum
import uuid
from sqlalchemy import Column, String, Float, Enum, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase

class StatusProposta(str, enum.Enum):
    NOVA = "NOVA"
    EM_ANALISE = "EM_ANALISE"
    APROVADA = "APROVADA"
    PERDIDA = "PERDIDA"

class Cliente(AuditableBase):
    """
    Representa um Cliente (Comprador de imóvel, etc) da Construtora.
    """
    __tablename__ = 'clientes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    cpf_cnpj = Column(String(20), nullable=True)
    renda_mensal = Column(Float, nullable=True)

class PropostaVenda(AuditableBase):
    """
    Representa uma intenção de compra de uma unidade atrelada à Obra.
    """
    __tablename__ = 'propostas_venda'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), index=True, nullable=False)
    cliente_id = Column(String(36), ForeignKey('clientes.id'), index=True, nullable=False)
    
    valor_negociado = Column(Float, nullable=False)
    unidade_descricao = Column(String(255), nullable=True)
    status = Column(Enum(StatusProposta), default=StatusProposta.NOVA, nullable=False)
    
    data_proposta = Column(Date, nullable=False)
    notas = Column(String, nullable=True)
