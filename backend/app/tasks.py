import logging
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.contexts.conectores_erp.conector_service import SincronizacaoService

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.sincronizar_todas_empresas")
def sincronizar_todas_empresas():
    """
    Cron Job que varre todos os workspaces e sincroniza Obras e Notas
    a partir dos conectores configurados (Sienge, etc).
    """
    logger.info("Iniciando rotina diária de sincronização (Celery Beat)")
    
    db = SessionLocal()
    try:
        # Por simplificacao no MVP, iteramos sobre empresas ativas.
        # Em producao veriamos na tabela Workspaces/Empresas.
        # Vamos rodar para a empresa default.
        empresa_id = "32ecbd0c-25d2-43bb-a30f-b1eaf602ed05"
        
        service = SincronizacaoService(db)
        
        logger.info(f"Sincronizando Obras da empresa {empresa_id}")
        obras_sync = service.sincronizar_obras(empresa_id)
        
        logger.info(f"Sincronizando Documentos da empresa {empresa_id}")
        docs_sync = service.sincronizar_documentos(empresa_id)
        
        logger.info(f"Sincronização concluída: {obras_sync.get('sincronizadas')} obras, {docs_sync.get('sincronizados')} documentos.")
        
        return {
            "status": "success",
            "obras": obras_sync.get('sincronizadas'),
            "documentos": docs_sync.get('sincronizados')
        }
        
    except Exception as e:
        logger.error(f"Erro na rotina de sincronizacao: {str(e)}")
        raise e
    finally:
        db.close()
