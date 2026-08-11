from typing import Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException

from app.core.uow import SQLAlchemyUnitOfWork
from app.models.fiscal import ApuracaoFiscal
from app.models.empresa_fiscal import EmpresaFiscal
from app.contexts.fiscal_engine.strategies.engine import TaxEngine

class ApurarImpostosPayload(BaseModel):
    competencia: str
    dados_faturamento: Dict[str, Any]

class ApurarImpostosCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, payload: ApurarImpostosPayload) -> ApuracaoFiscal:
        # Acesso seguro via Repositório para encontrar a empresa
        # Neste caso, como a TaxEngine precisa da EmpresaFiscal, vamos consultar a EmpresaFiscal.
        # EmpresaFiscal não está mapeada no uow ainda, mas podemos carregar diretamente
        # Pela segurança do UoW, o tenant_id está acessível.
        empresa = uow.session.query(EmpresaFiscal).filter(EmpresaFiscal.id == uow.tenant_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa Fiscal não encontrada ou não pertence ao tenant.")
            
        engine = TaxEngine(uow.session, empresa)
        
        # Engine não salva mais no banco, apenas retorna a entidade
        apuracao = engine.executar_calculo_mensal(payload.competencia, payload.dados_faturamento)
        
        # Persiste a apuração através do UoW / Repositório seguro
        uow.fiscal.create(uow.session, obj_in=apuracao.__dict__) # uow.fiscal.create handles dicts and objects
        # Wait, create in BaseRepository expects a dict or schema. 
        # But apuracao is an SQLAlchemy model instance. BaseRepository create usually receives a dict.
        # Alternatively, we can just add the model to the session directly since we have the instance.
        
        uow.session.add(apuracao)
        uow.commit()
        uow.session.refresh(apuracao)
        
        return apuracao
