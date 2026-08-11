from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.crm import Cliente, PropostaVenda, StatusProposta

router = APIRouter(prefix="/crm", tags=["crm"])

# Schemas
class ClienteCreate(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    renda_mensal: Optional[float] = None

class PropostaCreate(BaseModel):
    obra_id: str
    cliente_id: str
    valor_negociado: float
    unidade_descricao: Optional[str] = None
    data_proposta: date
    notas: Optional[str] = None

class PropostaUpdateStatus(BaseModel):
    status: StatusProposta

# Helpers
def _cliente_to_dict(c: Cliente) -> dict:
    return {
        "id": str(c.id),
        "nome": c.nome,
        "email": c.email,
        "telefone": c.telefone,
        "cpf_cnpj": c.cpf_cnpj,
        "renda_mensal": float(c.renda_mensal) if c.renda_mensal else None
    }

def _proposta_to_dict(p: PropostaVenda) -> dict:
    return {
        "id": str(p.id),
        "obra_id": str(p.obra_id),
        "cliente_id": str(p.cliente_id),
        "valor_negociado": float(p.valor_negociado),
        "unidade_descricao": p.unidade_descricao,
        "status": p.status.value,
        "data_proposta": p.data_proposta.isoformat(),
        "notas": p.notas
    }

# Endpoints
@router.get("/clientes", response_model=List[dict])
def list_clientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.modules.crm.queries.get_clientes import GetClientesQueryHandler
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    return GetClientesQueryHandler.execute(db, tenant_id)

@router.post("/clientes", response_model=dict, status_code=201)
def create_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.crm.commands.create_cliente import CreateClienteCommandHandler, ClienteCreatePayload
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = ClienteCreatePayload(**payload.dict())
        cliente = CreateClienteCommandHandler.execute(uow, cmd_payload)
        
    return _cliente_to_dict(cliente)

@router.get("/propostas", response_model=List[dict])
def list_propostas(
    obra_id: Optional[str] = Query(None),
    status: Optional[StatusProposta] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.modules.crm.queries.get_propostas import GetPropostasQueryHandler
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    return GetPropostasQueryHandler.execute(db, tenant_id, obra_id, status.value if status else None)

@router.post("/propostas", response_model=dict, status_code=201)
def create_proposta(
    payload: PropostaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.crm.commands.create_proposta import CreatePropostaCommandHandler, PropostaCreatePayload
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = PropostaCreatePayload(**payload.dict())
        proposta = CreatePropostaCommandHandler.execute(uow, cmd_payload)
        
    return _proposta_to_dict(proposta)

@router.patch("/propostas/{proposta_id}/status", response_model=dict)
def update_proposta_status(
    proposta_id: str,
    payload: PropostaUpdateStatus,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.crm.commands.update_proposta_status import UpdatePropostaStatusCommandHandler, PropostaUpdateStatusPayload
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = PropostaUpdateStatusPayload(status=payload.status)
        proposta = UpdatePropostaStatusCommandHandler.execute(uow, proposta_id, cmd_payload)
        
    return _proposta_to_dict(proposta)
