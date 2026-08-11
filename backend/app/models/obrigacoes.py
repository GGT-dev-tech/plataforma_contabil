import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase

class StatusObrigacao(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDO = "CONCLUIDO"
    ERRO = "ERRO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"

class TipoObrigacao(str, enum.Enum):
    SPED_ECD = "SPED_ECD"
    SPED_ECF = "SPED_ECF"
    DEFIS = "DEFIS"

class ObrigacaoAcessoriaJob(AuditableBase):
    """
    Rastreamento de background jobs de obrigações acessórias.
    Mapeia os metadados do processamento assíncrono.
    """
    __tablename__ = 'obrigacoes_acessorias_jobs'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    tipo = Column(Enum(TipoObrigacao), nullable=False)
    ano_calendario = Column(String(4), nullable=False)
    
    status = Column(Enum(StatusObrigacao), default=StatusObrigacao.PENDENTE, nullable=False)
    arquivo_url = Column(String(500), nullable=True) # S3 presigned url or local file path
    log_erros = Column(Text, nullable=True) # JSON ou texto livre com os erros do validador interno
    
    solicitado_por = Column(String(36), ForeignKey('usuarios.id'), nullable=True)

    empresa = relationship("Empresa")

class MapeamentoContaReferencial(AuditableBase):
    """
    Tabela de "De-Para" ligando o plano de contas analítico da Empresa 
    com o plano de contas Referencial da Receita Federal (SPED).
    """
    __tablename__ = 'mapeamentos_contas_referenciais'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=False, index=True)
    conta_interna_id = Column(UUID(as_uuid=True), ForeignKey('plano_de_contas.id'), nullable=False)
    
    # Ex: "1.01.01.01.01" - Conta Referencial do SPED
    codigo_conta_referencial = Column(String(50), nullable=False) 
    
    empresa = relationship("Empresa")
    conta_interna = relationship("PlanoDeContas")
