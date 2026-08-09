from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.financeiro import TituloFinanceiro, TipoTitulo, StatusTitulo

router = APIRouter(prefix="/financeiro", tags=["financeiro"])

class TituloCreate(BaseModel):
    tipo: TipoTitulo
    descricao: str
    fornecedor_cliente_nome: Optional[str] = None
    fornecedor_cliente_cnpj_cpf: Optional[str] = None
    valor_nominal: float
    data_emissao: date
    data_vencimento: date
    obra_id: Optional[str] = None

class TituloUpdateStatus(BaseModel):
    status: StatusTitulo
    data_pagamento: Optional[date] = None
    valor_pago: Optional[float] = None

def _titulo_to_dict(t: TituloFinanceiro) -> dict:
    return {
        "id": str(t.id),
        "empresa_id": str(t.empresa_id),
        "obra_id": str(t.obra_id) if t.obra_id else None,
        "documento_fiscal_id": t.documento_fiscal_id,
        "tipo": t.tipo.value,
        "status": t.status.value,
        "descricao": t.descricao,
        "fornecedor_cliente_nome": t.fornecedor_cliente_nome,
        "fornecedor_cliente_cnpj_cpf": t.fornecedor_cliente_cnpj_cpf,
        "valor_nominal": float(t.valor_nominal),
        "valor_pago": float(t.valor_pago),
        "data_emissao": t.data_emissao.isoformat(),
        "data_vencimento": t.data_vencimento.isoformat(),
        "data_pagamento": t.data_pagamento.isoformat() if t.data_pagamento else None,
        "gerado_automaticamente": t.gerado_automaticamente
    }

@router.get("/titulos", response_model=List[dict])
def list_titulos(
    empresa_id: Optional[str] = Query(None),
    obra_id: Optional[str] = Query(None),
    tipo: Optional[TipoTitulo] = Query(None),
    status: Optional[StatusTitulo] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(TituloFinanceiro)
    
    if current_user.role == Role.ADMIN:
        if empresa_id:
            query = query.filter(TituloFinanceiro.empresa_id == empresa_id)
    else:
        query = query.filter(TituloFinanceiro.empresa_id == current_user.empresa_id)
        
    if obra_id:
        query = query.filter(TituloFinanceiro.obra_id == obra_id)
    if tipo:
        query = query.filter(TituloFinanceiro.tipo == tipo)
    if status:
        query = query.filter(TituloFinanceiro.status == status)
        
    titulos = query.order_by(TituloFinanceiro.data_vencimento.asc()).limit(200).all()
    return [_titulo_to_dict(t) for t in titulos]

@router.post("/titulos", response_model=dict, status_code=201)
def create_titulo(
    payload: TituloCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.empresa_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    empresa_id = current_user.empresa_id
    # Admin precisaria passar a empresa de alguma forma (aqui simplificamos assumindo que ele já estaria logado numa empresa)
    
    titulo = TituloFinanceiro(
        empresa_id=empresa_id,
        obra_id=payload.obra_id,
        tipo=payload.tipo,
        status=StatusTitulo.ABERTO,
        descricao=payload.descricao,
        fornecedor_cliente_nome=payload.fornecedor_cliente_nome,
        fornecedor_cliente_cnpj_cpf=payload.fornecedor_cliente_cnpj_cpf,
        valor_nominal=payload.valor_nominal,
        data_emissao=payload.data_emissao,
        data_vencimento=payload.data_vencimento,
        gerado_automaticamente=False
    )
    
    db.add(titulo)
    db.commit()
    db.refresh(titulo)
    return _titulo_to_dict(titulo)

@router.patch("/titulos/{titulo_id}/status", response_model=dict)
def update_titulo_status(
    titulo_id: str,
    payload: TituloUpdateStatus,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    titulo = db.query(TituloFinanceiro).filter(TituloFinanceiro.id == titulo_id).first()
    if not titulo:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(titulo.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)
        
    titulo.status = payload.status
    if payload.data_pagamento:
        titulo.data_pagamento = payload.data_pagamento
    if payload.valor_pago is not None:
        titulo.valor_pago = payload.valor_pago
        
    db.commit()
    db.refresh(titulo)
    return _titulo_to_dict(titulo)
