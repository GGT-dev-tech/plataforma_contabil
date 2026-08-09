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


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Session):
        self.session = session
        self.executions = RepositoryExecucao(ExecucaoPipeline)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
