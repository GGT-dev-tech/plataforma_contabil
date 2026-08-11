from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.financeiro import TituloFinanceiro, TipoTitulo, StatusTitulo, MovimentacaoFinanceira, ConciliacaoFinanceira
from app.services.reconciliacao import ReconciliacaoService

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
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.financeiro.commands.update_titulo_status import UpdateTituloStatusCommandHandler, UpdateTituloStatusPayload
    
    # Valida Admin vs. Empresa: O Tenant ID é a empresa atual a menos que seja ADMIN (aí deixamos None para liberar, ou exigimos empresa alvo?)
    # Para simplificar na Rota Piloto: ADMIN = None, NORMAL = user.empresa_id
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    
    with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
        cmd_payload = UpdateTituloStatusPayload(
            status=payload.status,
            data_pagamento=payload.data_pagamento,
            valor_pago=payload.valor_pago
        )
        titulo = UpdateTituloStatusCommandHandler.execute(uow, titulo_id, cmd_payload)
        
    return _titulo_to_dict(titulo)

@router.post("/conciliar", response_model=dict)
def conciliar_titulos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Roda o Motor Algorítmico de Reconciliação (Fase 1, 2 e 3)
    para encontrar pares (Extrato <-> Fatura).
    """
    if not current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada")
        
    service = ReconciliacaoService(db)
    resultados = service.rodar_motor_conciliacao(str(current_user.empresa_id))
    return resultados

@router.get("/dre-gerencial", response_model=dict)
def dre_gerencial(
    mes: int = Query(None),
    ano: int = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna o relatório de DRE Gerencial (Baseado em Regime de Caixa).
    Soma todos os títulos liquidados no período fornecido.
    """
    if not current_user.empresa_id:
        raise HTTPException(status_code=403)
        
    query = db.query(TituloFinanceiro).filter(
        TituloFinanceiro.empresa_id == current_user.empresa_id,
        TituloFinanceiro.status == StatusTitulo.LIQUIDADO
    )
    
    if mes and ano:
        # Simplificação para SQLite/Postgres. Usando extract seria melhor, mas para MVP filtramos string ISO.
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano+1, 1, 1)
        else:
            data_fim = date(ano, mes+1, 1)
            
        query = query.filter(TituloFinanceiro.data_pagamento >= data_inicio)
        query = query.filter(TituloFinanceiro.data_pagamento < data_fim)
        
    titulos = query.all()
    
    receitas_por_categoria = {}
    despesas_por_categoria = {}
    
    total_receitas = 0.0
    total_despesas = 0.0
    
    for t in titulos:
        cat = t.categoria or "Sem Categoria"
        valor = t.valor_pago or 0.0
        if t.tipo == TipoTitulo.RECEBER:
            receitas_por_categoria[cat] = receitas_por_categoria.get(cat, 0.0) + valor
            total_receitas += valor
        else:
            despesas_por_categoria[cat] = despesas_por_categoria.get(cat, 0.0) + valor
            total_despesas += valor
            
    return {
        "regime": "CAIXA",
        "periodo": f"{mes:02d}/{ano}" if mes else "Geral",
        "receitas_operacionais": float(total_receitas),
        "despesas_operacionais": float(total_despesas),
        "resultado_liquido_caixa": float(total_receitas - total_despesas),
        "total_movimentos": len(titulos),
        "receitas_por_categoria": receitas_por_categoria,
        "despesas_por_categoria": despesas_por_categoria
    }
