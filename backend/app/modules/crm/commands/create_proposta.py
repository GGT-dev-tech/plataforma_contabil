from datetime import date
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.crm import PropostaVenda, StatusProposta

class PropostaCreatePayload(BaseModel):
    obra_id: str
    cliente_id: str
    valor_negociado: float
    unidade_descricao: Optional[str] = None
    data_proposta: date
    notas: Optional[str] = None

class CreatePropostaCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, payload: PropostaCreatePayload) -> PropostaVenda:
        if not uow.tenant_id:
            raise HTTPException(status_code=403, detail="Criação de proposta exige um tenant válido.")
            
        # Opcional: Validar se o cliente existe e pertence ao tenant
        cliente = uow.clientes.get(uow.session, payload.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado ou não pertence a este tenant.")
            
        proposta = PropostaVenda(
            empresa_id=uow.tenant_id,
            obra_id=payload.obra_id,
            cliente_id=payload.cliente_id,
            valor_negociado=payload.valor_negociado,
            unidade_descricao=payload.unidade_descricao,
            status=StatusProposta.NOVA,
            data_proposta=payload.data_proposta,
            notas=payload.notas
        )
        
        uow.session.add(proposta)
        uow.commit()
        uow.session.refresh(proposta)
        
        return proposta
