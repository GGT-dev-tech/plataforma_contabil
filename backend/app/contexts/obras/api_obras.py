"""
API de Obras — CRUD completo para gestão de empreendimentos.

Obras são centros de custo fundamentais para construtoras brasileiras.
Cada obra pode ter:
- Regime RET (patrimônio de afetação — Lei 10.931/2004)
- Matrícula CNO/CEI (INSS)
- Percentual de avanço físico (CPC 17)
- Sub-empreiteiros vinculados
"""
import uuid
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.obra import (
    Obra, Subempreiteiro, StatusObra, TipoObra, RegimeTributarioObra
)

router = APIRouter(prefix="/obras", tags=["obras"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ObraCreate(BaseModel):
    empresa_id: str
    nome: str
    codigo_interno: Optional[str] = None
    codigo_cno: Optional[str] = None
    endereco_obra: Optional[str] = None
    municipio_ibge: Optional[str] = None
    municipio_nome: Optional[str] = None
    uf: Optional[str] = None
    tipo: TipoObra = TipoObra.RESIDENCIAL
    patrimonio_afetacao: bool = False
    regime_tributario: RegimeTributarioObra = RegimeTributarioObra.NORMAL
    data_inicio: Optional[date] = None
    data_entrega_prevista: Optional[date] = None
    orcamento_total: Optional[float] = None
    receita_contratada_total: Optional[float] = None


class ObraUpdate(BaseModel):
    nome: Optional[str] = None
    status: Optional[StatusObra] = None
    codigo_cno: Optional[str] = None
    endereco_obra: Optional[str] = None
    municipio_ibge: Optional[str] = None
    municipio_nome: Optional[str] = None
    percentual_avanco_fisico: Optional[float] = None
    custo_incorrido_total: Optional[float] = None
    data_entrega_prevista: Optional[date] = None
    data_conclusao_real: Optional[date] = None
    observacoes: Optional[str] = None


def _obra_to_dict(obra: Obra) -> dict:
    return {
        "id": str(obra.id),
        "empresa_id": str(obra.empresa_id),
        "nome": obra.nome,
        "codigo_interno": obra.codigo_interno,
        "codigo_cno": obra.codigo_cno,
        "endereco_obra": obra.endereco_obra,
        "municipio_ibge": obra.municipio_ibge,
        "municipio_nome": obra.municipio_nome,
        "uf": obra.uf,
        "tipo": obra.tipo.value if obra.tipo else None,
        "status": obra.status.value if obra.status else None,
        "regime_tributario": obra.regime_tributario.value if obra.regime_tributario else None,
        "patrimonio_afetacao": obra.patrimonio_afetacao,
        "data_inicio": obra.data_inicio.isoformat() if obra.data_inicio else None,
        "data_entrega_prevista": obra.data_entrega_prevista.isoformat() if obra.data_entrega_prevista else None,
        "data_conclusao_real": obra.data_conclusao_real.isoformat() if obra.data_conclusao_real else None,
        "orcamento_total": float(obra.orcamento_total) if obra.orcamento_total else None,
        "receita_contratada_total": float(obra.receita_contratada_total) if obra.receita_contratada_total else None,
        "custo_incorrido_total": float(obra.custo_incorrido_total) if obra.custo_incorrido_total else 0,
        "percentual_avanco_fisico": float(obra.percentual_avanco_fisico) if obra.percentual_avanco_fisico else 0,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[dict])
def list_obras(
    empresa_id: Optional[str] = Query(None),
    status: Optional[StatusObra] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista obras da empresa. Admin vê todas, Analista vê apenas da sua empresa."""
    query = db.query(Obra)

    if current_user.role == Role.ADMIN:
        if empresa_id:
            query = query.filter(Obra.empresa_id == empresa_id)
    else:
        query = query.filter(Obra.empresa_id == current_user.empresa_id)

    if status:
        query = query.filter(Obra.status == status)

    obras = query.order_by(Obra.created_at.desc()).all()
    return [_obra_to_dict(o) for o in obras]


@router.get("/{obra_id}", response_model=dict)
def get_obra(
    obra_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra não encontrada")
    if current_user.role != Role.ADMIN and str(obra.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return _obra_to_dict(obra)


@router.post("", status_code=201, response_model=dict)
def create_obra(
    payload: ObraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403, detail="Permissão negada")

    obra = Obra(
        id=uuid.uuid4(),
        empresa_id=payload.empresa_id,
        nome=payload.nome,
        codigo_interno=payload.codigo_interno,
        codigo_cno=payload.codigo_cno,
        endereco_obra=payload.endereco_obra,
        municipio_ibge=payload.municipio_ibge,
        municipio_nome=payload.municipio_nome,
        uf=payload.uf,
        tipo=payload.tipo,
        status=StatusObra.EM_ANDAMENTO,
        regime_tributario=payload.regime_tributario,
        patrimonio_afetacao=payload.patrimonio_afetacao,
        data_inicio=payload.data_inicio,
        data_entrega_prevista=payload.data_entrega_prevista,
        orcamento_total=payload.orcamento_total,
        receita_contratada_total=payload.receita_contratada_total,
        custo_incorrido_total=0,
        percentual_avanco_fisico=0,
    )
    db.add(obra)
    db.commit()
    db.refresh(obra)
    return _obra_to_dict(obra)


@router.put("/{obra_id}", response_model=dict)
def update_obra(
    obra_id: str,
    payload: ObraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(obra.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obra, field, value)

    db.commit()
    db.refresh(obra)
    return _obra_to_dict(obra)


@router.patch("/{obra_id}/avanco", response_model=dict)
def atualizar_avanco_fisico(
    obra_id: str,
    percentual: float = Query(..., ge=0, le=100, description="Percentual de avanço físico (0-100)"),
    custo_incorrido: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza o percentual de avanço físico da obra (CPC 17 — POC).
    Essencial para reconhecimento de receita proporcional ao avanço.
    """
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(obra.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)

    obra.percentual_avanco_fisico = percentual
    if custo_incorrido is not None:
        obra.custo_incorrido_total = custo_incorrido
    if percentual >= 100:
        obra.status = StatusObra.CONCLUIDA

    db.commit()
    db.refresh(obra)
    return _obra_to_dict(obra)


@router.delete("/{obra_id}", status_code=204)
def delete_obra(
    obra_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir obras")
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404)
    db.delete(obra)
    db.commit()
