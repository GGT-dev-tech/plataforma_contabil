from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session

# Assume a declarative base exists or can be any type
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], tenant_id: Optional[str] = None):
        """
        Classe base CRUD genérica.
        :param model: Classe do modelo SQLAlchemy.
        :param tenant_id: Opcional, ID do tenant (empresa) para forçar isolamento Multi-Tenant.
        """
        self.model = model
        self.tenant_id = tenant_id

    def _apply_tenant_filter(self, query):
        if self.tenant_id and hasattr(self.model, "empresa_id"):
            from sqlalchemy.dialects.postgresql import UUID
            import uuid
            
            # Garantir conversão caso tenant_id seja string e empresa_id seja UUID
            try:
                tenant_uuid = uuid.UUID(self.tenant_id)
            except ValueError:
                tenant_uuid = self.tenant_id
                
            return query.filter(self.model.empresa_id == tenant_uuid)
        return query

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        query = db.query(self.model).filter(self.model.id == id)
        query = self._apply_tenant_filter(query)
        return query.first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = db.query(self.model)
        query = self._apply_tenant_filter(query)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.flush()
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.flush()
        return obj
