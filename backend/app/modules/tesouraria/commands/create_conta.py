from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.tesouraria import TesourariaContaBancaria

class ContaCreatePayload(BaseModel):
    banco: str
    agencia: Optional[str] = None
    conta: Optional[str] = None
    descricao: str
    saldo_inicial: float = 0.0

class CreateContaCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, payload: ContaCreatePayload) -> TesourariaContaBancaria:
        if not uow.tenant_id:
            # Em uma arquitetura real, administradores poderiam passar um tenant_id explícito
            raise HTTPException(status_code=403, detail="Criação de conta exige um tenant válido.")
            
        conta = TesourariaContaBancaria(
            empresa_id=uow.tenant_id,
            banco=payload.banco,
            agencia=payload.agencia,
            conta=payload.conta,
            descricao=payload.descricao,
            saldo_atual=payload.saldo_inicial
        )
        
        uow.session.add(conta)
        uow.commit()
        uow.session.refresh(conta)
        
        return conta
