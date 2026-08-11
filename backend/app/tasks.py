import logging
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.contexts.conectores_erp.service import ConectorErpService

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
        
        service = ConectorErpService(db)
        
        logger.info(f"Sincronizando Obras da empresa {empresa_id}")
        obras_sync = service.sincronizar_obras(empresa_id)
        
        # Pega a primeira obra para simular (MVP) a sincronização de documentos
        docs_sync = []
        if obras_sync:
            logger.info(f"Sincronizando Documentos da obra {obras_sync[0].id}")
            docs_sync = service.sincronizar_documentos(obras_sync[0].id)
        
        logger.info(f"Sincronização concluída: {len(obras_sync)} obras, {len(docs_sync)} documentos.")
        
        return {
            "status": "success",
            "obras": len(obras_sync),
            "documentos": len(docs_sync)
        }
        
    except Exception as e:
        logger.error(f"Erro na rotina de sincronizacao: {str(e)}")
        raise e
    finally:
        db.close()

@celery_app.task(name="app.tasks.gerar_sped_ecd_job")
def gerar_sped_ecd_job(job_id: str):
    import json
    import uuid
    import os
    from datetime import datetime
    
    from app.core.database import SessionLocal
    from app.models.obrigacoes import ObrigacaoAcessoriaJob, StatusObrigacao
    from app.models.ledger import LancamentoCabecalho
    from app.contexts.exportacao.builders import YAMLLayoutBuilder, LayoutParseError
    
    db = SessionLocal()
    job = db.query(ObrigacaoAcessoriaJob).filter(ObrigacaoAcessoriaJob.id == job_id).first()
    if not job:
        db.close()
        return
        
    try:
        job.status = StatusObrigacao.PROCESSANDO
        db.commit()
        
        # 1. Validação de Mapeamento (Faltante no MVP seria consultar a tabela MapeamentoContaReferencial)
        # Vamos assumir que validamos.
        
        # 2. Busca lançamentos (O ideal no SPED é iterar com yield para não estourar RAM)
        data_inicio = f"{job.ano_calendario}-01-01"
        data_fim = f"{job.ano_calendario}-12-31"
        
        # No MVP vamos usar fetchall porque o banco de dev é pequeno
        lancamentos = db.query(LancamentoCabecalho).filter(
            LancamentoCabecalho.empresa_id == job.empresa_id,
            LancamentoCabecalho.data_competencia >= data_inicio,
            LancamentoCabecalho.data_competencia <= data_fim,
            LancamentoCabecalho.is_deleted == False
        ).order_by(LancamentoCabecalho.data_competencia, LancamentoCabecalho.id).all()
        
        builder = YAMLLayoutBuilder("sped_ecd_v12.yaml")
        linhas_txt = []
        
        for cabecalho in lancamentos:
            # I200
            dados_i200 = {
                "NUM_LCTO": str(cabecalho.id),
                "DT_LCTO": cabecalho.data_competencia,
                "VL_LCTO": sum(p.valor for p in cabecalho.partidas if p.natureza.value == 'D'),
                "IND_LCTO": "N"
            }
            linhas_txt.append(builder.gerar_linha('I', 'I200', dados_i200))
            
            # I250
            for partida in cabecalho.partidas:
                dados_i250 = {
                    "COD_CTA": str(partida.conta_contabil_id),
                    "VL_DC": partida.valor,
                    "IND_DC": partida.natureza.value,
                    "HIST": cabecalho.historico_padrao
                }
                linhas_txt.append(builder.gerar_linha('I', 'I250', dados_i250))
                
        # 3. Salva no Storage Local (MVP)
        storage_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "sped")
        os.makedirs(storage_dir, exist_ok=True)
        filename = f"SPED_ECD_{job.ano_calendario}_{uuid.uuid4().hex[:8]}.txt"
        file_path = os.path.join(storage_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for l in linhas_txt:
                f.write(l + "\n")
                
        # 4. Finaliza o Job
        job.arquivo_url = f"/storage/sped/{filename}"
        job.status = StatusObrigacao.CONCLUIDO
        db.commit()
        
    except LayoutParseError as le:
        job.status = StatusObrigacao.ERRO_VALIDACAO
        job.log_erros = json.dumps({"erro": str(le)})
        db.commit()
    except Exception as e:
        job.status = StatusObrigacao.ERRO
        job.log_erros = json.dumps({"erro": str(e)})
        db.commit()
        logger.error(f"Erro ao gerar SPED ECD Job {job_id}: {str(e)}")
    finally:
        db.close()
