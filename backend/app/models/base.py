import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, MetaData
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

class AuditableBase(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    origem_sistema = Column(String, nullable=True) # Ex: SCI, INTER, PLANILHA
    arquivo_origem = Column(UUID(as_uuid=True), nullable=True) # Referencia ImportacaoArquivo
