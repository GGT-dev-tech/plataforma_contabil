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
    if not current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Usuário sem empresa vinculada.")
        
    empresa = db.query(EmpresaFiscal).filter(EmpresaFiscal.id == current_user.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa Fiscal não encontrada.")
        
    engine = TaxEngine(db, empresa)
    
    try:
        apuracao = engine.executar_calculo_mensal(payload.competencia, payload.dados_faturamento)
        return _apuracao_to_dict(apuracao)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/apuracoes", response_model=List[dict])
def list_apuracoes(
    competencia: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.empresa_id:
        raise HTTPException(status_code=403)
        
    query = db.query(ApuracaoFiscal).filter(ApuracaoFiscal.empresa_id == current_user.empresa_id)
    if competencia:
        query = query.filter(ApuracaoFiscal.competencia == competencia)
        
    apuracoes = query.order_by(ApuracaoFiscal.competencia.desc()).all()
    return [_apuracao_to_dict(a) for a in apuracoes]
