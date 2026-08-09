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
    query = db.query(Cliente)
    if current_user.role != Role.ADMIN:
        query = query.filter(Cliente.empresa_id == current_user.empresa_id)
    clientes = query.order_by(Cliente.nome.asc()).limit(100).all()
    return [_cliente_to_dict(c) for c in clientes]

@router.post("/clientes", response_model=dict, status_code=201)
def create_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.empresa_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    cliente = Cliente(
        empresa_id=current_user.empresa_id,
        nome=payload.nome,
        email=payload.email,
        telefone=payload.telefone,
        cpf_cnpj=payload.cpf_cnpj,
        renda_mensal=payload.renda_mensal
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return _cliente_to_dict(cliente)

@router.get("/propostas", response_model=List[dict])
def list_propostas(
    obra_id: Optional[str] = Query(None),
    status: Optional[StatusProposta] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(PropostaVenda, Cliente).join(Cliente, PropostaVenda.cliente_id == Cliente.id)
    
    if current_user.role != Role.ADMIN:
        query = query.filter(PropostaVenda.empresa_id == current_user.empresa_id)
        
    if obra_id:
        query = query.filter(PropostaVenda.obra_id == obra_id)
    if status:
        query = query.filter(PropostaVenda.status == status)
        
    results = query.order_by(PropostaVenda.data_proposta.desc()).all()
    
    propostas = []
    for prop, cli in results:
        d = _proposta_to_dict(prop)
        d["cliente_nome"] = cli.nome
        propostas.append(d)
        
    return propostas

@router.post("/propostas", response_model=dict, status_code=201)
def create_proposta(
    payload: PropostaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.empresa_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    proposta = PropostaVenda(
        empresa_id=current_user.empresa_id,
        obra_id=payload.obra_id,
        cliente_id=payload.cliente_id,
        valor_negociado=payload.valor_negociado,
        unidade_descricao=payload.unidade_descricao,
        status=StatusProposta.NOVA,
        data_proposta=payload.data_proposta,
        notas=payload.notas
    )
    db.add(proposta)
    db.commit()
    db.refresh(proposta)
    return _proposta_to_dict(proposta)

@router.patch("/propostas/{proposta_id}/status", response_model=dict)
def update_proposta_status(
    proposta_id: str,
    payload: PropostaUpdateStatus,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    proposta = db.query(PropostaVenda).filter(PropostaVenda.id == proposta_id).first()
    if not proposta:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(proposta.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)
        
    proposta.status = payload.status
    db.commit()
    db.refresh(proposta)
    return _proposta_to_dict(proposta)
