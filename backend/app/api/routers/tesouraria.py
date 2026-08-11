from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.tesouraria import TesourariaContaBancaria, TesourariaTransacao, TipoTransacao

router = APIRouter(prefix="/tesouraria", tags=["tesouraria"])

class ContaCreate(BaseModel):
    banco: str
    agencia: Optional[str] = None
    conta: Optional[str] = None
    descricao: str
    saldo_inicial: float = 0.0

class TransacaoCreate(BaseModel):
    conta_bancaria_id: str
    data_transacao: date
    tipo: TipoTransacao
    valor: float
    descricao: str

def _conta_to_dict(c: TesourariaContaBancaria) -> dict:
    return {
        "id": str(c.id),
        "banco": c.banco,
        "agencia": c.agencia,
        "conta": c.conta,
        "descricao": c.descricao,
        "saldo_atual": float(c.saldo_atual)
    }

def _transacao_to_dict(t: TesourariaTransacao, conta_desc: str = "") -> dict:
    return {
        "id": str(t.id),
        "conta_bancaria_id": str(t.conta_bancaria_id),
        "conta_descricao": conta_desc,
        "data_transacao": t.data_transacao.isoformat(),
        "tipo": t.tipo.value,
        "valor": float(t.valor),
        "descricao": t.descricao
    }

@router.get("/contas", response_model=List[dict])
def list_contas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.modules.tesouraria.queries.get_contas import GetContasQueryHandler
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    return GetContasQueryHandler.execute(db, tenant_id)

@router.post("/contas", response_model=dict, status_code=201)
def create_conta(
    payload: ContaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.tesouraria.commands.create_conta import CreateContaCommandHandler, ContaCreatePayload
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = ContaCreatePayload(**payload.dict())
        conta = CreateContaCommandHandler.execute(uow, cmd_payload)
        
    return _conta_to_dict(conta)

@router.get("/transacoes", response_model=List[dict])
def list_transacoes(
    conta_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.modules.tesouraria.queries.get_transacoes import GetTransacoesQueryHandler
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    return GetTransacoesQueryHandler.execute(db, tenant_id, conta_id)

@router.post("/transacoes", response_model=dict, status_code=201)
def create_transacao(
    payload: TransacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.tesouraria.commands.create_transacao import CreateTransacaoCommandHandler, TransacaoCreatePayload
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = TransacaoCreatePayload(**payload.dict())
        transacao = CreateTransacaoCommandHandler.execute(uow, cmd_payload)
        
        # O CommandHandler já garante que a conta existe e retorna a transacao.
        # Precisamos do nome da conta pro retorno dict
        conta = uow.contas.get(uow.session, transacao.conta_bancaria_id)
        
    return _transacao_to_dict(transacao, conta.descricao if conta else "")
