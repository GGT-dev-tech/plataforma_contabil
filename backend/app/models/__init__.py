from .base import Base, AuditableBase

# ── Núcleo ativo de domain.py ─────────────────────────────────────────────────
from .domain import (
    Empresa,
    ContaBancaria,
    ContaContabil,
    Fornecedor,
    Projeto,
    CategoriaFinanceira,
    ClientSchemaMapping,
    ImportacaoArquivo,
    Conciliacao,
    ConciliacaoItem,
    ConciliacaoExplicacao,
    ExecucaoPipeline,
    StatusExecucao,
    StagingRegistro,
    TipoStaging,
    TipoArquivo,
    Role,
    Usuario,
    WorkspaceMember,
    StatusConciliacao,
    TipoMatch,
    MatchCandidate,
    StatusCandidato,
    CandidateEvaluationLog,
    ContaFinanceira,
    TipoContaFinanceira,
    Receita,
)

# ── Sprint 1: Módulos TO-BE ────────────────────────────────────────────────────
from .empresa_fiscal import EmpresaFiscal, RegimeTributario
from .obra import Obra, Subempreiteiro, RegimeTributarioObra, StatusObra, TipoObra
from .financeiro import TituloFinanceiro, StatusTitulo, TipoTitulo, MovimentacaoFinanceira, TipoMovimentacao, ConciliacaoFinanceira
from .documento_fiscal import (
    DocumentoFiscalV2,
    ParcelaDocumentoFiscal,
    TipoDocumentoFiscal,
    NaturezaOperacao,
    StatusDocumentoFiscal,
)
from .plano_contas import (
    PlanoDeContas,
    RegraFiscalMunicipio,
    TabelaIRRF,
    NaturezaConta,
    TipoConta,
    GrupoConta,
)
from .ledger import (
    LancamentoCabecalho,
    PartidaItem,
    PeriodoContabil,
    TemplateLancamento,
    TipoPartida,
    StatusLancamento,
    StatusPeriodo,
    ModuloOrigem,
)
from .obrigacoes import (
    ObrigacaoAcessoriaJob,
    MapeamentoContaReferencial,
    StatusObrigacao,
    TipoObrigacao,
)
from .fiscal import ApuracaoFiscal, DetalheImposto, TipoImposto

__all__ = [
    # Base
    "Base", "AuditableBase",
    # Domain Core
    "Empresa", "ContaBancaria", "ContaContabil", "Fornecedor", "Projeto",
    "CategoriaFinanceira", "ClientSchemaMapping",
    "ImportacaoArquivo", "Conciliacao", "ConciliacaoItem", "ConciliacaoExplicacao",
    "ExecucaoPipeline", "StatusExecucao", "StagingRegistro", "TipoStaging",
    "TipoArquivo", "Role", "Usuario", "WorkspaceMember",
    "StatusConciliacao", "TipoMatch",
    "MatchCandidate", "StatusCandidato", "CandidateEvaluationLog",
    "ContaFinanceira", "TipoContaFinanceira", "Receita",
    # Novos
    "EmpresaFiscal", "RegimeTributario",
    "Obra", "Subempreiteiro", "RegimeTributarioObra", "StatusObra", "TipoObra",
    "TituloFinanceiro", "StatusTitulo", "TipoTitulo", "MovimentacaoFinanceira", "TipoMovimentacao", "ConciliacaoFinanceira",
    "DocumentoFiscalV2", "ParcelaDocumentoFiscal",
    "TipoDocumentoFiscal", "NaturezaOperacao", "StatusDocumentoFiscal",
    "PlanoDeContas", "RegraFiscalMunicipio", "TabelaIRRF",
    "NaturezaConta", "TipoConta", "GrupoConta",
    "LancamentoCabecalho", "PartidaItem", "PeriodoContabil", 
    "TemplateLancamento", "TipoPartida", "StatusLancamento", "StatusPeriodo", "ModuloOrigem",
    "ObrigacaoAcessoriaJob", "MapeamentoContaReferencial", "StatusObrigacao", "TipoObrigacao",
    "ApuracaoFiscal", "DetalheImposto", "TipoImposto",
]
