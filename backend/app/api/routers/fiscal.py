from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.empresa_fiscal import EmpresaFiscal
from app.models.fiscal import ApuracaoFiscal, DetalheImposto
from app.contexts.fiscal_engine.strategies.engine import TaxEngine

router = APIRouter(prefix="/fiscal", tags=["fiscal"])

class ApuracaoRequest(BaseModel):
    competencia: str
    dados_faturamento: Dict[str, Any]

def _detalhe_to_dict(d: DetalheImposto) -> dict:
    return {
        "id": str(d.id),
        "tipo_imposto": d.tipo_imposto.value,
        "base_de_calculo": float(d.base_de_calculo),
        "aliquota": float(d.aliquota),
        "valor_apurado": float(d.valor_apurado),
        "valor_retido": float(d.valor_retido),
        "valor_a_pagar": float(d.valor_a_pagar)
    }

def _apuracao_to_dict(a: ApuracaoFiscal) -> dict:
    return {
        "id": str(a.id),
        "empresa_id": str(a.empresa_id),
        "competencia": a.competencia,
        "faturamento_total": float(a.faturamento_total),
        "imposto_devido": float(a.imposto_devido),
        "detalhes": [_detalhe_to_dict(d) for d in a.detalhes]
    }

@router.post("/apurar", response_model=dict, status_code=201)
def apurar_impostos(
    payload: ApuracaoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.fiscal.commands.apurar_impostos import ApurarImpostosCommandHandler, ApurarImpostosPayload
    
    if not current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    with SQLAlchemyUnitOfWork(db, tenant_id=str(current_user.empresa_id)) as uow:
        cmd_payload = ApurarImpostosPayload(
            competencia=payload.competencia,
            dados_faturamento=payload.dados_faturamento
        )
        apuracao = ApurarImpostosCommandHandler.execute(uow, cmd_payload)
        
    return _apuracao_to_dict(apuracao)

@router.get("/apuracoes", response_model=List[dict])
def list_apuracoes(
    competencia: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.modules.fiscal.queries.get_apuracoes import GetApuracoesQueryHandler
    
    if not current_user.empresa_id:
        raise HTTPException(status_code=403)
        
    return GetApuracoesQueryHandler.execute(db, str(current_user.empresa_id), competencia)
