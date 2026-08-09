from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db
from app.contexts.exportacao.service import ExportacaoService

router = APIRouter(
    prefix="/exportacao",
    tags=["exportacao"]
)

@router.get("/lancamentos")
def exportar_lancamentos(
    formato: str = Query("dominio_sistemas", description="Formato de exportação (ex: dominio_sistemas)"),
    empresa_id: Optional[str] = Query(None, description="Filtrar por empresa"),
    obra_id: Optional[str] = Query(None, description="Filtrar por obra"),
    db: Session = Depends(get_db)
):
    """
    Gera um arquivo de exportação dos lançamentos contábeis gerados,
    pronto para ser importado no ERP contábil selecionado.
    """
    service = ExportacaoService(db)
    
    try:
        conteudo_bytes = service.exportar_arquivos(formato, empresa_id, obra_id)
        
        extensao = "txt"
        if formato in service.adapters:
            extensao = service.adapters[formato].get_extensao_arquivo()
            
        filename = f"exportacao_contabil_{formato}.{extensao}"
        
        return Response(
            content=conteudo_bytes,
            media_type="text/plain; charset=windows-1252",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno na exportação: {str(e)}")
