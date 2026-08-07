import abc
import logging
from fastapi import BackgroundTasks
import traceback
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PipelineRunner(abc.ABC):
    @abc.abstractmethod
    def run(self, execucao_id: str):
        """Inicia o processamento do pipeline (pode ser síncrono ou assíncrono dependendo da implementação)"""
        pass

class SyncRunner(PipelineRunner):
    """MVP: Roda no BackgroundTasks do FastAPI. Futuro: CeleryRunner"""
    def __init__(self, background_tasks: BackgroundTasks, db_session: Session):
        self.background_tasks = background_tasks
        self.db = db_session
        
    def run(self, execucao_id: str):
        def _bg_task():
            from app.api.deps import SessionLocal
            db = SessionLocal()
            try:
                execute_pipeline_core(execucao_id, db)
            finally:
                db.close()
        self.background_tasks.add_task(_bg_task)

class CeleryRunner(PipelineRunner):
    """Executa no Celery + Redis (Assíncrono e Resiliente)"""
    def run(self, execucao_id: str):
        from app.worker import run_pipeline_task
        run_pipeline_task.delay(execucao_id)

def execute_pipeline_core(execucao_id: str, db: Session):
        from app.engine.core import MatchOrchestrator
        from app.models.domain import ExecucaoPipeline, StatusExecucao
        import json
        
        try:
            execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == execucao_id).first()
            if not execucao:
                logger.error(f"Execução {execucao_id} não encontrada.")
                return
                
            # Recupera caminhos dos arquivos e roda parsers
            from app.models.domain import ImportacaoArquivo
            importacoes = db.query(ImportacaoArquivo).filter(ImportacaoArquivo.execucao_id == execucao_id).all()
            
            from app.services.parsers import ParserFactory
            
            for imp in importacoes:
                logger.info(f"Procurando parser para o arquivo {imp.tipo} - {imp.nome_original}")
                parser = ParserFactory.get_parser(imp.storage_path, imp.tipo)
                if parser:
                    logger.info(f"Parser encontrado: {parser.__class__.__name__}. Iniciando processamento...")
                    parser.parse(imp.storage_path, db, execucao_id)
                else:
                    logger.warning(f"Nenhum parser encontrado para {imp.nome_original} (Tipo: {imp.tipo})")
            
            # Agora executa o motor
            orchestrator = MatchOrchestrator(db, execucao_id=execucao_id)
            stats = orchestrator.run_pipeline()
            logger.info(f"Pipeline concluído: {stats}")
            
        except Exception as e:
            logger.error(f"Erro no pipeline {execucao_id}: {e}")
            execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == execucao_id).first()
            if execucao:
                execucao.status = StatusExecucao.ERRO
                execucao.erro_codigo = type(e).__name__
                execucao.erro_mensagem = str(e)
                import traceback
                execucao.erro_stacktrace = traceback.format_exc()
                db.commit()
