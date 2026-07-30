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
        self.background_tasks.add_task(self._execute_pipeline_task, execucao_id)
        
    def _execute_pipeline_task(self, execucao_id: str):
        from app.engine.core import MatchOrchestrator
        from app.models.domain import ExecucaoPipeline, StatusExecucao
        import json
        
        # Como é rodado numa nova task, precisamos recarregar o obj e gerenciar sessões cuidadosamente.
        # No MVP, usaremos self.db mas o ideal é criar nova Session
        
        try:
            execucao = self.db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == execucao_id).first()
            if not execucao:
                logger.error(f"Execução {execucao_id} não encontrada.")
                return
                
            # Recupera caminhos dos arquivos e roda parsers
            from app.models.domain import ImportacaoArquivo
            importacoes = self.db.query(ImportacaoArquivo).filter(ImportacaoArquivo.execucao_id == execucao_id).all()
            
            from app.services.parsers import ParserFactory
            
            for imp in importacoes:
                logger.info(f"Procurando parser para o arquivo {imp.tipo} - {imp.nome_original}")
                parser = ParserFactory.get_parser(imp.storage_path, imp.tipo)
                if parser:
                    logger.info(f"Parser encontrado: {parser.__class__.__name__}. Iniciando processamento...")
                    parser.parse(imp.storage_path, self.db, execucao_id)
                else:
                    logger.warning(f"Nenhum parser encontrado para {imp.nome_original} (Tipo: {imp.tipo})")
            
            # Agora executa o motor
            orchestrator = MatchOrchestrator(self.db, execucao_id=execucao_id)
            stats = orchestrator.run_pipeline()
            logger.info(f"Pipeline concluído: {stats}")
            
        except Exception as e:
            logger.error(f"Erro no pipeline {execucao_id}: {e}")
            if execucao:
                execucao.status = StatusExecucao.ERRO
                execucao.erro_codigo = type(e).__name__
                execucao.erro_mensagem = str(e)
                execucao.erro_stacktrace = traceback.format_exc()
                self.db.commit()
