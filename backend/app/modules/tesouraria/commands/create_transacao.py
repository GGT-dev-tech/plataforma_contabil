from datetime import date
from pydantic import BaseModel
from fastapi import HTTPException
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.tesouraria import TesourariaTransacao, TipoTransacao

class TransacaoCreatePayload(BaseModel):
    conta_bancaria_id: str
    data_transacao: date
    tipo: TipoTransacao
    valor: float
    descricao: str

class CreateTransacaoCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, payload: TransacaoCreatePayload) -> TesourariaTransacao:
        if not uow.tenant_id:
            raise HTTPException(status_code=403, detail="Criação de transação exige um tenant válido.")
            
        # Repositório garante a verificação silenciosa do tenant_id (empresa_id) 
        # Acesso seguro
        conta = uow.contas.get(uow.session, payload.conta_bancaria_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta bancária não encontrada ou não pertence a este tenant.")
            
        transacao = TesourariaTransacao(
            empresa_id=uow.tenant_id,
            conta_bancaria_id=conta.id,
            data_transacao=payload.data_transacao,
            tipo=payload.tipo,
            valor=payload.valor,
            descricao=payload.descricao
        )
        
        # O UoW vai garantir que o insert e o update de saldo sejam atômicos (ACID)
        # Se ocorrer qualquer erro, nada será persistido.
        if payload.tipo == TipoTransacao.ENTRADA:
            conta.saldo_atual += payload.valor
        else:
            conta.saldo_atual -= payload.valor
            
        uow.session.add(transacao)
        uow.commit()
        uow.session.refresh(transacao)
        
        return transacao
