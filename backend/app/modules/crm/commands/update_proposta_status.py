from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.crm import PropostaVenda, StatusProposta

class PropostaUpdateStatusPayload(BaseModel):
    status: StatusProposta

class UpdatePropostaStatusCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, proposta_id: str, payload: PropostaUpdateStatusPayload) -> PropostaVenda:
        proposta = uow.propostas.get(uow.session, proposta_id)
        if not proposta:
            raise HTTPException(status_code=404, detail="Proposta não encontrada ou não pertence a este tenant.")
            
        proposta.status = payload.status
        
        uow.commit()
        uow.session.refresh(proposta)
        
        return proposta
