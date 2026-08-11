from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role

router = APIRouter(
    prefix="/sincronizacao",
    tags=["sincronizacao_erp"]
)

@router.post("/obras", response_model=Dict[str, int])
def sincronizar_obras(
    erp_name: str = Query("sienge", description="Nome do ERP (ex: sienge)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Força a sincronização de obras/centros de custo a partir do ERP.
    """
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.sincronizacao.commands.sync_obras import SyncObrasCommandHandler
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Sincronização exige um tenant_id (empresa) válido.")
        
    try:
        with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
            novas_obras = SyncObrasCommandHandler.execute(uow, erp_name)
        return {"novas_obras_importadas": len(novas_obras)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")

@router.post("/documentos", response_model=Dict[str, int])
def sincronizar_documentos(
    obra_id: str = Query(..., description="ID da Obra interna"),
    erp_name: str = Query("sienge", description="Nome do ERP (ex: sienge)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Força a sincronização de Documentos Fiscais para uma Obra a partir do ERP.
    """
    from app.core.uow import SQLAlchemyUnitOfWork
    from app.modules.sincronizacao.commands.sync_documentos import SyncDocumentosCommandHandler
    
    tenant_id = None if current_user.role == Role.ADMIN else str(current_user.empresa_id)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Sincronização exige um tenant_id (empresa) válido.")
        
    try:
        with SQLAlchemyUnitOfWork(db, tenant_id=tenant_id) as uow:
            novos_docs = SyncDocumentosCommandHandler.execute(uow, obra_id, erp_name)
        return {"novos_documentos_importados": len(novos_docs)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")
