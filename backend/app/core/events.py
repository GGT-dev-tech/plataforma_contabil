import logging

logger = logging.getLogger(__name__)

class EventBus:
    @staticmethod
    def publish(event_name: str, **kwargs):
        logger.info(f"Event published: {event_name} with payload: {kwargs}")
        
        if event_name == "FilesIngestedEvent":
            exec_id = kwargs.get("exec_id")
            if exec_id:
                from app.contexts.matching_auditing.worker import run_pipeline_task
                # Dispara a tarefa assíncrona no Message Broker (Redis/Celery)
                run_pipeline_task.delay(exec_id)
                logger.info(f"Dispatched run_pipeline_task to Celery for exec_id {exec_id}")
                
        elif event_name == "MatchDecisionEvent":
            cand_id = kwargs.get("cand_id")
            action = kwargs.get("action")
            logger.info(f"[EDA] Evento de Auditoria recebido. Match {cand_id} foi {action}. ERP Externo notificado.")
            
            if action == "APROVAR":
                from app.contexts.matching_auditing.engine.accounting_generator import generate_accounting_entry
                import threading
                # Para evitar delay na API, executamos em background (ou Celery na infra real)
                threading.Thread(target=generate_accounting_entry, args=(cand_id,)).start()
