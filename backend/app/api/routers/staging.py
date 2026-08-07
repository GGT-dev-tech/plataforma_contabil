import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth import get_current_user
from app.models.domain import Usuario, StagingRegistro, StatusExecucao
from app.core.uow import SQLAlchemyUnitOfWork
from app.services.staging_service import StagingService
from app.services.template_service import generate_standard_template
from app.services.parsers.standard_parser import StandardTemplateParser
from app.api import schemas

router = APIRouter(tags=["staging"])

@router.get("/templates/standard")
def download_standard_template():
    content = generate_standard_template()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Planilha_Padrao_Contabil.xlsx"}
    )

@router.post("/executions/{exec_id}/import-standard")
def import_standard_template(exec_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404, detail="Execução não encontrada")

        parser = StandardTemplateParser()
        parsed_items = parser.parse(file.file)

        staging_models = []
        for item in parsed_items:
            data_obj = datetime.strptime(item["data"], "%Y-%m-%d").date() if isinstance(item["data"], str) else item["data"]
            reg = StagingRegistro(
                id=str(uuid.uuid4()),
                execucao_id=exec_id,
                tipo=item["tipo"],
                data=data_obj,
                descricao=item.get("descricao") or "Sem Descrição",
                valor=item.get("valor") or 0.0,
                entidade_nome=item.get("entidade_nome"),
                cnpj_cpf=item.get("cnpj_cpf"),
                categoria=item.get("categoria"),
                conta_origem=item.get("conta_origem"),
                conta_destino=item.get("conta_destino"),
                forma_pagamento=item.get("forma_pagamento")
            )
            staging_models.append(reg)

        uow.session.add_all(staging_models)
        execucao.status = StatusExecucao.ARQUIVOS_ANEXADOS
        uow.commit()
    return {"message": f"Importados {len(staging_models)} registros para área de staging com sucesso.", "total": len(staging_models)}

@router.get("/executions/{exec_id}/staging")
def get_staging_records(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        records = uow.session.query(StagingRegistro).filter(StagingRegistro.execucao_id == exec_id).order_by(StagingRegistro.data.asc()).all()
        return records

@router.put("/executions/{exec_id}/staging/{item_id}")
def update_staging_record(exec_id: str, item_id: str, data: schemas.StagingUpdateSchema, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        item = uow.session.query(StagingRegistro).filter(StagingRegistro.id == item_id, StagingRegistro.execucao_id == exec_id).first()
        if not item: raise HTTPException(status_code=404, detail="Item de staging não encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        uow.commit()
        uow.session.refresh(item)
        return item

@router.delete("/executions/{exec_id}/staging/{item_id}")
def delete_staging_record(exec_id: str, item_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        item = uow.session.query(StagingRegistro).filter(StagingRegistro.id == item_id, StagingRegistro.execucao_id == exec_id).first()
        if not item: raise HTTPException(status_code=404, detail="Item não encontrado")
        uow.session.delete(item)
        uow.commit()
    return {"message": "Registro removido do staging"}

@router.post("/executions/{exec_id}/staging/process")
def process_staging(exec_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    with SQLAlchemyUnitOfWork(db) as uow:
        execucao = uow.executions.get(uow.session, exec_id)
        if not execucao: raise HTTPException(status_code=404, detail="Execução não encontrada")

        staging_items = uow.executions.get_staging_pendentes(uow.session, exec_id)
        if not staging_items:
            raise HTTPException(status_code=400, detail="Nenhum item pendente no staging para processar")

        service = StagingService(uow.session)
        result = service.process_staging_items(exec_id, staging_items)
        
        # StagingService internally calls db.commit(), but here we respect UoW boundary.
        # Ideally, we would adapt StagingService to not commit if UoW is managing it, 
        # but for now, we leave it as is or do an explicit uow.commit().
        uow.commit()

    return {
        "message": "Staging processado com sucesso com apuração fiscal e conciliação 3-Way",
        "tax_summary": result["tax_summary"],
        "match_stats": result["match_stats"]
    }
