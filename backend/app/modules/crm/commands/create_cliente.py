from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.crm import Cliente

class ClienteCreatePayload(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    renda_mensal: Optional[float] = None

class CreateClienteCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, payload: ClienteCreatePayload) -> Cliente:
        if not uow.tenant_id:
            raise HTTPException(status_code=403, detail="Criação de cliente exige um tenant válido.")
            
        cliente = Cliente(
            empresa_id=uow.tenant_id,
            nome=payload.nome,
            email=payload.email,
            telefone=payload.telefone,
            cpf_cnpj=payload.cpf_cnpj,
            renda_mensal=payload.renda_mensal
        )
        
        uow.session.add(cliente)
        uow.commit()
        uow.session.refresh(cliente)
        
        return cliente
