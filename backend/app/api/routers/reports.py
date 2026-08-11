from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from typing import Optional
from starlette.responses import Response

from app.api.deps import get_db
from app.contexts.accounting.dre_service import DREService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/reports",
    tags=["Reports"]
)

@router.get("/dre")
def get_dre_report(
    workspace_id: UUID,
    ano: int,
    mes: Optional[int] = None,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """
    Retorna o DRE consolidado do workspace (empresa_id).
    Se 'mes' for fornecido, retorna o DRE daquele mês específico.
    Caso contrário, retorna o DRE consolidado anual (acumulado + mensal).
    """
    service = DREService(db)
    
    if mes:
        import calendar
        _, last_day = calendar.monthrange(ano, mes)
        dt_inicio = date(ano, mes, 1)
        dt_fim = date(ano, mes, last_day)
        dre = service.calcular_dre_periodo(workspace_id, dt_inicio, dt_fim)
        return {"ano": ano, "mes": mes, "dre": dre}
    else:
        return service.calcular_acumulado_ano(workspace_id, ano)

@router.get("/dre/download")
def download_dre_report(
    workspace_id: UUID,
    ano: int,
    mes: Optional[int] = None,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """
    Baixa o DRE consolidado em formato Excel.
    """
    service = DREService(db)
    
    if mes:
        import calendar
        _, last_day = calendar.monthrange(ano, mes)
        dt_inicio = date(ano, mes, 1)
        dt_fim = date(ano, mes, last_day)
        dados = service.calcular_dre_periodo(workspace_id, dt_inicio, dt_fim)
        periodo_str = f"{mes:02d}/{ano}"
    else:
        # Se for o ano todo, pega o acumulado
        relatorio = service.calcular_acumulado_ano(workspace_id, ano)
        dados = relatorio["acumulado"]
        periodo_str = f"Acumulado {ano}"
        
    excel_bytes = service.exportar_excel(dados, periodo_str)
    
    filename = f"DRE_{workspace_id}_{ano}_{mes if mes else 'anual'}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(
        content=excel_bytes, 
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
