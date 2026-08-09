"""
Módulo: Empresa (Workspace)
Expansão do modelo original para suportar regime tributário completo,
inscrições fiscais e metadados do escritório contábil.
"""
from sqlalchemy import Column, String, Enum, Boolean, Numeric
from app.models.base import AuditableBase
import enum


class RegimeTributario(str, enum.Enum):
    """Regimes tributários brasileiros relevantes para construtoras."""
    SIMPLES_NACIONAL = "SIMPLES_NACIONAL"
    LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO"
    LUCRO_REAL = "LUCRO_REAL"
    RET = "RET"  # Regime Especial de Tributação - Lei 10.931/2004 (Patrimônio de Afetação)
    ISENTO = "ISENTO"


class EmpresaFiscal(AuditableBase):
    """
    Extensão fiscal da entidade Empresa.
    Armazena dados tributários e de inscrição da construtora.
    
    Decisão de design: mantemos a tabela 'empresas' original e criamos
    esta tabela de extensão com FK 1:1, para não quebrar o código existente.
    """
    __tablename__ = 'empresas_fiscal'

    empresa_id = Column(String(36), nullable=False, unique=True, index=True)

    # Regime Tributário
    regime_tributario = Column(
        Enum(RegimeTributario),
        default=RegimeTributario.LUCRO_PRESUMIDO,
        nullable=False
    )

    # Identificadores Fiscais
    codigo_cnae_principal = Column(String(10), nullable=True)  # Ex: 4120-4/00 (construção de edif. res.)
    inscricao_estadual = Column(String(30), nullable=True)
    inscricao_municipal = Column(String(30), nullable=True)  # Necessário para NFS-e

    # Município Sede (define a alíquota padrão de ISS)
    municipio_ibge = Column(String(7), nullable=True)  # Código IBGE de 7 dígitos
    municipio_nome = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)

    # Configurações de Retenção
    optante_simples = Column(Boolean, default=False)
    contribuinte_icms = Column(Boolean, default=False)
    sujeito_retencao_iss = Column(Boolean, default=True)
    sujeito_retencao_inss = Column(Boolean, default=True)

    # Configurações de Sistema Contábil de Destino
    # Define qual adapter usar para exportação (dominio, alterdata, sped, planilha)
    sistema_contabil_destino = Column(String(50), nullable=True)
    config_exportacao = Column(String, nullable=True)  # JSON serializado
