from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, Enum, ForeignKey, UniqueConstraint, DateTime, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import date, datetime
import enum
import uuid
from .base import AuditableBase

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    ANALISTA = "ANALISTA"
    AUDITOR = "AUDITOR"

class Usuario(AuditableBase):
    __tablename__ = 'usuarios'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    nome = Column(String(255))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True) # Nullable para usuarios admin/globais
    role = Column(Enum(Role), default=Role.ANALISTA)
    is_active = Column(Boolean, default=True)

    workspaces = relationship("WorkspaceMember", back_populates="usuario", cascade="all, delete-orphan")

class Empresa(AuditableBase):
    __tablename__ = 'empresas'
    cnpj = Column(String, unique=True, index=True)
    razao_social = Column(String)
    nome_fantasia = Column(String)
    import_config = Column(JSON, nullable=True)

    membros = relationship("WorkspaceMember", back_populates="empresa", cascade="all, delete-orphan")

class WorkspaceMember(AuditableBase):
    __tablename__ = 'workspace_members'
    usuario_id = Column(String(36), ForeignKey('usuarios.id'), index=True, nullable=False)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    role = Column(Enum(Role), default=Role.ANALISTA)
    
    usuario = relationship("Usuario", back_populates="workspaces")
    empresa = relationship("Empresa", back_populates="membros")

class ClientSchemaMapping(AuditableBase):
    __tablename__ = 'client_schema_mappings'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), index=True, nullable=False)
    # Assinatura gerada pelas colunas originais do arquivo (ex: sha256 de "Data,Fornecedor,Valor")
    file_signature = Column(String(255), index=True, nullable=False)
    # JSON contendo o De-Para, ex: {"Data de competência": "data", "Fornecedor": "descricao"}
    mapping_json = Column(JSON, nullable=False)

class ContaBancaria(AuditableBase):
    __tablename__ = 'contas_bancarias'
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'))
    banco = Column(String)
    agencia = Column(String)
    conta = Column(String)
    tipo = Column(String)
    
    empresa = relationship("Empresa")

class ContaContabil(AuditableBase):
    __tablename__ = 'contas_contabeis'
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'))
    codigo_contabil = Column(String, index=True)
    descricao = Column(String)
    natureza = Column(String) # D ou C

class Fornecedor(AuditableBase):
    __tablename__ = 'fornecedores'
    cnpj_cpf = Column(String, index=True)
    nome = Column(String)
    nome_normalizado = Column(String, index=True)

class Projeto(AuditableBase):
    __tablename__ = 'projetos'
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'))
    nome = Column(String)
    codigo_externo = Column(String, index=True)

class CategoriaFinanceira(AuditableBase):
    __tablename__ = 'categorias_financeiras'
    nome = Column(String)

class TipoArquivo(str, enum.Enum):
    DESPESA = "DESPESA"
    EXTRATO = "EXTRATO"
    RAZAO = "RAZAO"

class StatusExecucao(str, enum.Enum):
    CRIADA = "CRIADA"
    ARQUIVOS_ANEXADOS = "ARQUIVOS_ANEXADOS"
    PROCESSANDO = "PROCESSANDO"
    AGUARDANDO_REVISAO_STAGING = "AGUARDANDO_REVISAO_STAGING"
    CONCILIANDO = "CONCILIANDO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"

class ExecucaoPipeline(AuditableBase):
    __tablename__ = "execucoes_pipeline"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True) # Nullable for backward compatibility during dev, but should be enforced logically
    status = Column(Enum(StatusExecucao), default=StatusExecucao.CRIADA, nullable=False)
    
    # Inputs/Config
    matching_profile = Column(String(100))
    runtime_profile = Column(String(100))
    
    # Analytics / Relatório
    data_inicio = Column(DateTime, default=datetime.utcnow)
    data_fim = Column(DateTime, nullable=True)
    duracao_ms = Column(Float, nullable=True)
    hashes_arquivos = Column(Text, nullable=True) # Salvo como string de JSON
    tax_summary = Column(JSON, nullable=True) # Impostos e Totais
    
    # Erro de Job
    erro_codigo = Column(String(100), nullable=True)
    erro_mensagem = Column(Text, nullable=True)
    erro_stacktrace = Column(Text, nullable=True)

class ImportacaoArquivo(AuditableBase):
    __tablename__ = 'importacoes_arquivo'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execucao_id = Column(String(36), ForeignKey('execucoes_pipeline.id'), nullable=False)
    nome_original = Column(String, nullable=False)
    tipo = Column(Enum(TipoArquivo), nullable=False)
    
    storage_path = Column(String, nullable=False)
    hash_sha256 = Column(String, nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)
    
    uploaded_by = Column(String(100), nullable=True) # ID do Usuário
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    execucao = relationship("ExecucaoPipeline")

class StatusConciliacao(str, enum.Enum):
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"

class TipoMatch(str, enum.Enum):
    UM_PARA_UM = "1:1"
    UM_PARA_N = "1:N"
    N_PARA_UM = "N:1"
    N_PARA_M = "N:M"

class Conciliacao(AuditableBase):
    __tablename__ = "conciliacoes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(StatusConciliacao), nullable=False)
    tipo_match = Column(Enum(TipoMatch), nullable=False)
    score_match = Column(Integer, nullable=True) # 0 a 100
    regra_utilizada = Column(String(100), nullable=True) # ex: "ValueAndDateRule"
    
    # Auditabilidade e Versionamento
    matching_profile = Column(String(100), nullable=True) # ex: financeiro_2026
    explainability_version = Column(String(50), nullable=True) # ex: 1.0.0
    
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_aprovacao = Column(DateTime, nullable=True)
    aprovado_por = Column(String(100), nullable=True)
    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    itens = relationship("ConciliacaoItem", back_populates="conciliacao", cascade="all, delete-orphan")
    explicacoes = relationship("ConciliacaoExplicacao", back_populates="conciliacao", cascade="all, delete-orphan")

class ConciliacaoItem(AuditableBase):
    __tablename__ = "conciliacoes_itens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conciliacao_id = Column(String(36), ForeignKey("conciliacoes.id"), nullable=False)
    
    # Entidades vinculadas (todas opcionais, pois depende do lado do match)
    titulo_id = Column(String(36), ForeignKey("titulos_financeiros.id"), nullable=True)
    movimentacao_financeira_id = Column(String(36), ForeignKey("movimentacoes_financeiras.id"), nullable=True)
    lancamento_cabecalho_id = Column(UUID(as_uuid=True), ForeignKey("lancamentos_cabecalhos.id"), nullable=True)

    # Relacionamentos
    conciliacao = relationship("Conciliacao", back_populates="itens")
    titulo = relationship("TituloFinanceiro")
    movimentacao_financeira = relationship("MovimentacaoFinanceira")
    lancamento = relationship("LancamentoCabecalho")

class ConciliacaoExplicacao(AuditableBase):
    __tablename__ = "conciliacao_explicacoes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conciliacao_id = Column(String(36), ForeignKey("conciliacoes.id"), nullable=False)
    regra = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    peso = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    justificativa = Column(Text, nullable=False)
    
    # Auditabilidade e Versionamento
    matching_profile = Column(String(100), nullable=True)
    explainability_version = Column(String(50), nullable=True)
    
    conciliacao = relationship("Conciliacao", back_populates="explicacoes")

class StatusCandidato(str, enum.Enum):
    PENDENTE_REVISAO = "PENDENTE_REVISAO"
    REJEITADO_PELO_MOTOR = "REJEITADO_PELO_MOTOR"
    APROVADO = "APROVADO"

class CandidateEvaluationLog(AuditableBase):
    __tablename__ = "candidate_evaluation_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execucao_id = Column(String(36), ForeignKey("execucoes_pipeline.id"), nullable=False)
    movimentacao_financeira_id = Column(String(36), ForeignKey('movimentacoes_financeiras.id'), nullable=False)
    titulo_id = Column(String(36), ForeignKey('titulos_financeiros.id'), nullable=True)
    lancamento_cabecalho_id = Column(UUID(as_uuid=True), ForeignKey('lancamentos_cabecalhos.id'), nullable=True)
    regra = Column(String(100), nullable=False)
    motivo_descarte = Column(Text, nullable=False)
    
class MatchCandidate(AuditableBase):
    """Representa um candidato avaliado pelo motor antes da decisão final"""
    __tablename__ = "match_candidates"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execucao_id = Column(String(36), ForeignKey("execucoes_pipeline.id"), nullable=False)
    movimentacao_financeira_id = Column(String(36), ForeignKey('movimentacoes_financeiras.id'), nullable=False)
    titulo_id = Column(String(36), ForeignKey('titulos_financeiros.id'), nullable=True)
    lancamento_cabecalho_id = Column(UUID(as_uuid=True), ForeignKey('lancamentos_cabecalhos.id'), nullable=True)
    
    score_total = Column(Float, nullable=False)
    status = Column(Enum(StatusCandidato), nullable=False)
    motivo_descarte = Column(Text, nullable=True)
    
    # A auditoria completa baseada em snapshot de score/rules 
    explanation_snapshot = Column(Text, nullable=True) # Salvo como string de JSON
    
    # Decisão Humana
    reviewed_by = Column(String(36), ForeignKey("usuarios.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    decision_comment = Column(Text, nullable=True)
    
    execucao = relationship("ExecucaoPipeline")
    movimentacao = relationship("MovimentacaoFinanceira")
    titulo = relationship("TituloFinanceiro")
    lancamento = relationship("LancamentoCabecalho")
    revisor = relationship("Usuario")

class TipoContaFinanceira(str, enum.Enum):
    BANCO = "BANCO"
    CAIXA_ESPECIE = "CAIXA_ESPECIE"
    CARTAO_CREDITO = "CARTAO_CREDITO"

class ContaFinanceira(AuditableBase):
    __tablename__ = 'contas_financeiras'
    nome = Column(String(100), nullable=False) # Ex: Banco Inter, Caixa Geral (Dinheiro)
    tipo = Column(Enum(TipoContaFinanceira), default=TipoContaFinanceira.BANCO, nullable=False)
    banco_codigo = Column(String(10), nullable=True) # Ex: 077
    agencia = Column(String(20), nullable=True)
    numero_conta = Column(String(30), nullable=True)
    saldo_inicial = Column(Numeric(15, 2), default=0.0)

class TipoStaging(str, enum.Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"
    EXTRATO = "EXTRATO"
    DINHEIRO = "DINHEIRO"

class StagingRegistro(AuditableBase):
    """Área de staging para edição CRUD dos dados importados da planilha padrão antes do cálculo"""
    __tablename__ = 'staging_registro'
    id = Column(String(50), primary_key=True)
    execucao_id = Column(String(50), ForeignKey('execucoes_pipeline.id'), index=True)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True)
    tipo = Column(Enum(TipoStaging), nullable=False)
    
    data = Column(Date, nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(15, 2), nullable=False)
    
    # Detalhes opcionais por tipo
    entidade_nome = Column(String(255), nullable=True) # Cliente ou Fornecedor
    cnpj_cpf = Column(String(30), nullable=True)
    categoria = Column(String(100), nullable=True)
    conta_origem = Column(String(100), nullable=True)
    conta_destino = Column(String(100), nullable=True)
    forma_pagamento = Column(String(50), nullable=True) # PIX, BOLETO, DINHEIRO, TED
    
    # Status de edição no Staging
    processado = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)

class Receita(AuditableBase):
    __tablename__ = 'receitas'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execucao_id = Column(String(36), ForeignKey('execucoes_pipeline.id'), nullable=True)
    cliente_nome = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    valor_total = Column(Numeric(15, 2), nullable=False)
    data_emissao = Column(Date, nullable=False)
    data_recebimento = Column(Date, nullable=True)
    forma_pagamento = Column(String(50), nullable=True)
    conta_destino = Column(String(100), nullable=True)

