"""
Módulo: Obras e Centros de Custo
Essencial para o segmento de construção civil brasileiro.

Fundamentos regulatórios:
- Lei 10.931/2004: Patrimônio de Afetação → RET (4% unificado)
- Matrícula CNO/CEI (INSS) obrigatória por obra
- CPC 17: Reconhecimento de receita por percentual de completude (POC)
- Separação contábil por obra no regime RET
"""
from sqlalchemy import Column, String, Date, Numeric, Boolean, Enum, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase
import enum


class RegimeTributarioObra(str, enum.Enum):
    """
    Regime tributário específico por obra.
    Uma empresa pode ter obras em RET e outras não simultaneamente.
    """
    RET = "RET"            # Patrimônio de afetação: 4% unificado sobre receita bruta
    NORMAL = "NORMAL"      # Tributação pelo regime da empresa-mãe
    ISENTO = "ISENTO"      # Obras de interesse social (PMCMV etc.)


class StatusObra(str, enum.Enum):
    PLANEJAMENTO = "PLANEJAMENTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    PARALISADA = "PARALISADA"
    CONCLUIDA = "CONCLUIDA"
    ENTREGUE = "ENTREGUE"


class TipoObra(str, enum.Enum):
    RESIDENCIAL = "RESIDENCIAL"
    COMERCIAL = "COMERCIAL"
    INDUSTRIAL = "INDUSTRIAL"
    INFRAESTRUTURA = "INFRAESTRUTURA"
    REFORMA = "REFORMA"
    MISTA = "MISTA"


class Obra(AuditableBase):
    """
    Centro de custo principal para construtoras.
    
    Cada obra é uma unidade de acumulação de custos e,
    quando em regime de patrimônio de afetação, uma entidade
    contábil praticamente independente.
    
    Referências:
    - ABNT NBR 12.721 (memorial descritivo)
    - Lei 10.931/2004 (patrimônio de afetação)
    - Instrução Normativa RFB 971/2009 (INSS obra)
    """
    __tablename__ = 'obras'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)

    # Identificação
    nome = Column(String(255), nullable=False)
    codigo_interno = Column(String(50), nullable=True, index=True)  # Código interno da construtora

    # Matrícula INSS (CNO - Cadastro Nacional de Obras)
    # Obrigatório pela IN RFB 971/2009 para obras com mão de obra própria
    codigo_cno = Column(String(20), nullable=True, unique=True, index=True)  # Formato: 00.000.00000/00-00
    codigo_cei = Column(String(20), nullable=True)  # CEI antigo (ainda usado em algumas situações)

    # Localização (município define a alíquota de ISS)
    endereco_obra = Column(String(255), nullable=True)
    municipio_ibge = Column(String(7), nullable=True)
    municipio_nome = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)

    # Classificação
    tipo = Column(Enum(TipoObra), default=TipoObra.RESIDENCIAL, nullable=False)
    status = Column(Enum(StatusObra), default=StatusObra.EM_ANDAMENTO, nullable=False)

    # Datas
    data_inicio = Column(Date, nullable=True)
    data_entrega_prevista = Column(Date, nullable=True)
    data_conclusao_real = Column(Date, nullable=True)

    # Regime Tributário Específico
    patrimonio_afetacao = Column(Boolean, default=False, nullable=False)
    regime_tributario = Column(
        Enum(RegimeTributarioObra),
        default=RegimeTributarioObra.NORMAL,
        nullable=False
    )

    # Financeiro/Físico (atualizado mensalmente para cálculo POC - CPC 17)
    orcamento_total = Column(Numeric(18, 2), nullable=True)
    custo_incorrido_total = Column(Numeric(18, 2), default=0, nullable=False)
    receita_contratada_total = Column(Numeric(18, 2), nullable=True)
    percentual_avanco_fisico = Column(Numeric(5, 2), default=0)  # 0.00 a 100.00

    # Conta bancária vinculada (obrigatório no RET - conta separada por obra)
    conta_bancaria_afetacao = Column(String(50), nullable=True)

    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    empresa = relationship("Empresa")
    documentos_fiscais = relationship("DocumentoFiscal", back_populates="obra")


class Subempreiteiro(AuditableBase):
    """
    Pessoa física ou jurídica contratada para execução parcial de uma obra.
    Tratamento fiscal específico: retenção ISS, INSS e IRRF conforme natureza.
    """
    __tablename__ = 'subempreiteiros'

    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), nullable=False)
    fornecedor_id = Column(UUID(as_uuid=True), ForeignKey('fornecedores.id'), nullable=False)

    tipo_contrato = Column(String(30), nullable=True)  # EMPREITADA_GLOBAL, EMPREITADA_PARCIAL, ADMINISTRACAO
    valor_contrato = Column(Numeric(18, 2), nullable=True)
    data_contrato = Column(Date, nullable=True)
    objeto_contrato = Column(Text, nullable=True)

    obra = relationship("Obra")
    fornecedor = relationship("Fornecedor")
