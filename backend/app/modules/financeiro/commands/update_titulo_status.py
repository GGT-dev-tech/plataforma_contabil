from typing import Optional
from datetime import date
from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.financeiro import StatusTitulo, TituloFinanceiro

class UpdateTituloStatusPayload(BaseModel):
    status: StatusTitulo
    data_pagamento: Optional[date] = None
    valor_pago: Optional[float] = None

class UpdateTituloStatusCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, titulo_id: str, payload: UpdateTituloStatusPayload) -> TituloFinanceiro:
        # Acesso seguro via Repositório, que já injetou o filtro Multi-Tenant (empresa_id) silenciosamente.
        titulo = uow.titulos.get(uow.session, titulo_id)
        if not titulo:
            raise HTTPException(status_code=404, detail="Título não encontrado ou não pertence a esta empresa.")
            
        titulo.status = payload.status
        if payload.data_pagamento:
            titulo.data_pagamento = payload.data_pagamento
        if payload.valor_pago is not None:
            titulo.valor_pago = payload.valor_pago
            
        uow.commit()
        uow.session.refresh(titulo)
        
        return titulo
