from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import with_loader_criteria
from .config import settings
from .tenant import get_tenant_id

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(SessionLocal, "do_orm_execute")
def _add_tenant_filter(execute_state):
    """
    Intercepta as queries do SQLAlchemy e adiciona o filtro de tenant_id.
    """
    tenant_id = get_tenant_id()
    if tenant_id and not execute_state.is_column_load and not execute_state.is_relationship_load:
        # Tenta aplicar criteria para cada entidade da query que tenha 'empresa_id'
        # (Nós ainda não mudamos tudo para tenant_id, então usa empresa_id)
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                lambda cls: hasattr(cls, "empresa_id"),
                lambda cls: cls.empresa_id == tenant_id,
                include_aliases=True
            )
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
