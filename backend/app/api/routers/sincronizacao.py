from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from app.api.deps import get_db
from app.contexts.conectores_erp.service import ConectorErpService

router = APIRouter(
    prefix="/sincronizacao",
    tags=["sincronizacao_erp"]
)

@router.post("/obras", response_model=Dict[str, int])
def sincronizar_obras(
    empresa_id: str = Query(..., description="ID da Empresa"),
    erp_name: str = Query("sienge", description="Nome do ERP (ex: sienge)"),
    db: Session = Depends(get_db)
):
    """
    Força a sincronização de obras/centros de custo a partir do ERP.
    """
    service = ConectorErpService(db)
    try:
        novas_obras = service.sincronizar_obras(empresa_id, erp_name)
        return {"novas_obras_importadas": len(novas_obras)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")

@router.post("/documentos", response_model=Dict[str, int])
def sincronizar_documentos(
    obra_id: str = Query(..., description="ID da Obra interna"),
    erp_name: str = Query("sienge", description="Nome do ERP (ex: sienge)"),
    db: Session = Depends(get_db)
):
    """
    Força a sincronização de Documentos Fiscais para uma Obra a partir do ERP.
    """
    service = ConectorErpService(db)
    try:
        novos_docs = service.sincronizar_documentos(obra_id, erp_name)
        return {"novos_documentos_importados": len(novos_docs)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")
