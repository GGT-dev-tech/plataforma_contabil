from .base import Base, AuditableBase

# ── Módulo legado (mantido para compatibilidade) ──────────────────────────────
from .domain import (
    Empresa,
    ContaBancaria,
    ContaContabil,
    Fornecedor,
    Projeto,
    CategoriaFinanceira,
    ExtratoBancario,
    MovimentacaoBancaria,
    Despesa,
    ParcelaDespesa,
    DocumentoFiscal,        # legado (documentos_fiscais) – manter para MV existente
    LancamentoContabil,     # legado – manter
    ImportacaoArquivo,
    Conciliacao,
    Pagamento,
    ConciliacaoItem,
    ExecucaoPipeline,
    StatusExecucao,
    StagingRegistro,
    TipoStaging,
    TipoArquivo,
    Role,
    Usuario,
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
    # Legado
    "Empresa", "ContaBancaria", "ContaContabil", "Fornecedor", "Projeto",
    "CategoriaFinanceira", "ExtratoBancario", "MovimentacaoBancaria",
    "Despesa", "ParcelaDespesa", "DocumentoFiscal", "LancamentoContabil",
    "ImportacaoArquivo", "Conciliacao", "Pagamento", "ConciliacaoItem",
    "ExecucaoPipeline", "StatusExecucao", "StagingRegistro", "TipoStaging",
    "TipoArquivo", "Role", "Usuario",
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
