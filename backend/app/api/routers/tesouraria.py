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
    query = db.query(TesourariaContaBancaria)
    if current_user.role != Role.ADMIN:
        query = query.filter(TesourariaContaBancaria.empresa_id == current_user.empresa_id)
    contas = query.all()
    return [_conta_to_dict(c) for c in contas]

@router.post("/contas", response_model=dict, status_code=201)
def create_conta(
    payload: ContaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.empresa_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    conta = TesourariaContaBancaria(
        empresa_id=current_user.empresa_id,
        banco=payload.banco,
        agencia=payload.agencia,
        conta=payload.conta,
        descricao=payload.descricao,
        saldo_atual=payload.saldo_inicial
    )
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return _conta_to_dict(conta)

@router.get("/transacoes", response_model=List[dict])
def list_transacoes(
    conta_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(TesourariaTransacao, TesourariaContaBancaria).join(TesourariaContaBancaria, TesourariaTransacao.conta_bancaria_id == TesourariaContaBancaria.id)
    
    if current_user.role != Role.ADMIN:
        query = query.filter(TesourariaTransacao.empresa_id == current_user.empresa_id)
        
    if conta_id:
        query = query.filter(TesourariaTransacao.conta_bancaria_id == conta_id)
        
    results = query.order_by(TesourariaTransacao.data_transacao.desc()).limit(100).all()
    return [_transacao_to_dict(t, c.descricao) for t, c in results]

@router.post("/transacoes", response_model=dict, status_code=201)
def create_transacao(
    payload: TransacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    conta = db.query(TesourariaContaBancaria).filter(TesourariaContaBancaria.id == payload.conta_bancaria_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    if current_user.role != Role.ADMIN and str(conta.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)
        
    transacao = TesourariaTransacao(
        empresa_id=conta.empresa_id,
        conta_bancaria_id=conta.id,
        data_transacao=payload.data_transacao,
        tipo=payload.tipo,
        valor=payload.valor,
        descricao=payload.descricao
    )
    
    # Atualiza saldo
    if payload.tipo == TipoTransacao.ENTRADA:
        conta.saldo_atual += payload.valor
    else:
        conta.saldo_atual -= payload.valor
        
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return _transacao_to_dict(transacao, conta.descricao)
