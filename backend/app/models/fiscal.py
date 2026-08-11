import uuid
import enum
from sqlalchemy import Column, String, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import AuditableBase

class TipoImposto(str, enum.Enum):
    IRPJ = "IRPJ"
    CSLL = "CSLL"
    PIS = "PIS"
    COFINS = "COFINS"
    ISS = "ISS"
    INSS = "INSS"
    SIMPLES_NACIONAL = "SIMPLES_NACIONAL"
    MEI_DAS = "MEI_DAS"

class ApuracaoFiscal(AuditableBase):
    """
    Cabeçalho da Apuração Mensal (Motor Fiscal)
    """
    __tablename__ = 'apuracoes_fiscais'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    
    competencia = Column(String(7), nullable=False) # Formato YYYY-MM
    faturamento_total = Column(Float, nullable=False, default=0.0)
    imposto_devido = Column(Float, nullable=False, default=0.0) # Total a pagar na guia (DAS ou DARFs)
    
    # Relação com os detalhes da apuração
    detalhes = relationship("DetalheImposto", back_populates="apuracao", cascade="all, delete-orphan")

class DetalheImposto(AuditableBase):
    """
    Discriminação de cada imposto gerado no mês ou retenção abatida.
    """
    __tablename__ = 'detalhes_impostos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    apuracao_id = Column(String(36), ForeignKey('apuracoes_fiscais.id'), nullable=False)
    
    tipo_imposto = Column(Enum(TipoImposto), nullable=False)
    base_de_calculo = Column(Float, nullable=False, default=0.0)
    aliquota = Column(Float, nullable=False, default=0.0)
    
    valor_apurado = Column(Float, nullable=False, default=0.0)
    valor_retido = Column(Float, nullable=False, default=0.0)
    valor_a_pagar = Column(Float, nullable=False, default=0.0)
    
    apuracao = relationship("ApuracaoFiscal", back_populates="detalhes")
