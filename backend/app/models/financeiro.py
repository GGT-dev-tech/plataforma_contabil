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
    PAGO = "PAGO"
    ATRASADO = "ATRASADO"
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
    documento_fiscal_id = Column(String(36), ForeignKey('documentos_fiscais_v2.id'), nullable=True)
    
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
