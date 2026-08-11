import abc
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PipelineRunner(abc.ABC):
    @abc.abstractmethod
    def run(self, execucao_id: str):
        """Inicia o processamento do pipeline (pode ser síncrono ou assíncrono dependendo da implementação)"""
        pass

class CeleryRunner(PipelineRunner):
    """Executa no Celery + Redis (Assíncrono e Resiliente)"""
    def run(self, execucao_id: str):
        from app.contexts.matching_auditing.worker import run_pipeline_task
        run_pipeline_task.delay(execucao_id)

def execute_pipeline_core(execucao_id: str, db: Session):
        from app.contexts.matching_auditing.engine.core import MatchOrchestrator
        from app.models.domain import ExecucaoPipeline, StatusExecucao
        import json
        
        try:
            execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == execucao_id).first()
            if not execucao:
                logger.error(f"Execução {execucao_id} não encontrada.")
                return
                
            if execucao.status == StatusExecucao.PROCESSANDO:
                # ETAPA 1: Parsing para Staging
                from app.models.domain import ImportacaoArquivo, Empresa
                importacoes = db.query(ImportacaoArquivo).filter(ImportacaoArquivo.execucao_id == execucao_id).all()
                empresa = db.query(Empresa).filter(Empresa.id == execucao.empresa_id).first()
                import_config = empresa.import_config if empresa else None
                
                from app.contexts.staging_ingestion.parsers import ParserFactory
                
                for imp in importacoes:
                    logger.info(f"Procurando parser para o arquivo {imp.tipo} - {imp.nome_original}")
                    parser = ParserFactory.get_parser(imp.storage_path, imp.tipo, import_config=import_config)
                    if parser:
                        logger.info(f"Parser encontrado: {parser.__class__.__name__}. Iniciando processamento...")
                        parser.parse(imp.storage_path, db, execucao_id)
                    else:
                        logger.warning(f"Nenhum parser encontrado para {imp.nome_original} (Tipo: {imp.tipo})")
                
                execucao.status = StatusExecucao.AGUARDANDO_REVISAO_STAGING
                db.commit()
                logger.info(f"Pipeline fase 1 (Parsing) concluído. Aguardando revisão no Frontend.")
                
            elif execucao.status == StatusExecucao.CONCILIANDO:
                # ETAPA 2: Normalização, Enrichment e Matching
                logger.info(f"Pipeline fase 2 iniciada para execução {execucao_id}.")
                
                # 2.1 Processar Staging para o Domínio
                from app.contexts.staging_ingestion.service import StagingService
                from app.models.domain import StagingRegistro
                from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro
                
                staging_items = db.query(StagingRegistro).filter(
                    StagingRegistro.execucao_id == execucao_id, 
                    StagingRegistro.processado == False
                ).all()
                
                if staging_items:
                    staging_service = StagingService(db)
                    staging_service.process_staging_items(execucao_id, staging_items)
                    db.commit()
                    logger.info(f"Convertidos {len(staging_items)} registros de Staging.")
                
                # 2.2 Enriquecimento
                from app.services.enrichment import EnrichmentService
                execucao_obj = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == execucao_id).first()
                empresa_id = execucao_obj.empresa_id if execucao_obj else None
                if empresa_id:
                    movs = db.query(MovimentacaoFinanceira).filter(MovimentacaoFinanceira.empresa_id == empresa_id, MovimentacaoFinanceira.conciliada == False).all()
                    titulos = db.query(TituloFinanceiro).filter(TituloFinanceiro.empresa_id == empresa_id).all()
                    
                    EnrichmentService.enrich_movimentacoes(movs)
                    EnrichmentService.enrich_titulos(titulos)
                    db.commit()
                    logger.info("Enriquecimento de dados concluído.")
                
                # 2.3 Matching Engine
                orchestrator = MatchOrchestrator(db, execucao_id=execucao_id)
                stats = orchestrator.run_pipeline()
                logger.info(f"Pipeline fase 2 concluído: {stats}")
            
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
