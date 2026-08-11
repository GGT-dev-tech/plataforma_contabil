from __future__ import annotations
import abc
from sqlalchemy.orm import Session
from app.repositories.execution_repository import RepositoryExecucao
from app.models.domain import ExecucaoPipeline

class AbstractUnitOfWork(abc.ABC):
    executions: RepositoryExecucao

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


from app.models.financeiro import TituloFinanceiro
from app.repositories.financeiro_repository import TituloRepository

from app.models.fiscal import ApuracaoFiscal
from app.repositories.fiscal_repository import FiscalRepository

from app.models.tesouraria import TesourariaContaBancaria, TesourariaTransacao
from app.repositories.base import BaseRepository

from app.models.crm import Cliente, PropostaVenda

from app.models.obra import Obra
from app.models.documento_fiscal import DocumentoFiscalV2

from app.models.obrigacoes import ObrigacaoAcessoriaJob

class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Session, tenant_id: str = None):
        self.session = session
        self.tenant_id = tenant_id
        
        # Registra os repositórios injetando o tenant_id para segurança
        self.executions = RepositoryExecucao(ExecucaoPipeline, tenant_id=tenant_id)
        self.titulos = TituloRepository(TituloFinanceiro, tenant_id=tenant_id)
        self.fiscal = FiscalRepository(ApuracaoFiscal, tenant_id=tenant_id)
        self.contas = BaseRepository(TesourariaContaBancaria, tenant_id=tenant_id)
        self.transacoes = BaseRepository(TesourariaTransacao, tenant_id=tenant_id)
        self.clientes = BaseRepository(Cliente, tenant_id=tenant_id)
        self.propostas = BaseRepository(PropostaVenda, tenant_id=tenant_id)
        self.obras = BaseRepository(Obra, tenant_id=tenant_id)
        self.documentos = BaseRepository(DocumentoFiscalV2, tenant_id=tenant_id)
        self.obrigacoes_jobs = BaseRepository(ObrigacaoAcessoriaJob, tenant_id=tenant_id)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
