import uuid
from typing import Dict, Any
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.obrigacoes import ObrigacaoAcessoriaJob, TipoObrigacao, StatusObrigacao
from app.tasks import gerar_sped_ecd_job

class RequestSpedEcdCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, ano: str) -> Dict[str, Any]:
        if not uow.tenant_id:
            raise ValueError("SPED exige um tenant_id válido.")
            
        job = ObrigacaoAcessoriaJob(
            id=str(uuid.uuid4()),
            empresa_id=uow.tenant_id,
            tipo=TipoObrigacao.SPED_ECD,
            ano_calendario=ano,
            status=StatusObrigacao.PENDENTE
        )
        
        uow.session.add(job)
        uow.commit() # Garante que o Job foi salvo no banco ANTES do Celery tentar ler
        uow.session.refresh(job)
        
        # Enfileira tarefa no Celery. A partir daqui o Job ID existe.
        gerar_sped_ecd_job.delay(str(job.id))
        
        return {"message": "Job enfileirado com sucesso", "job_id": str(job.id)}
