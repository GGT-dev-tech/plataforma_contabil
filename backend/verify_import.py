import os
import uuid
import sys
import logging
from sqlalchemy.orm import Session
from app.api.deps import SessionLocal
from app.models.domain import TipoArquivo, ExecucaoPipeline, ImportacaoArquivo, Despesa, ParcelaDespesa, MovimentacaoBancaria, LancamentoContabil
from app.pipeline.runner import PipelineRunner
from app.services.parsers import ParserFactory

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def verify():
    db = SessionLocal()
    exec_id = str(uuid.uuid4())
    execucao = ExecucaoPipeline(id=exec_id, status="CRIADA")
    db.add(execucao)
    db.commit()

    base_dir = "Architecture" if os.path.exists("Architecture") else "../Architecture"
    files_to_test = [
        ("Despesas 06-2026.xlsx", TipoArquivo.DESPESA),
        ("Extrato-01-06-2026-a-30-06-2026-PDF.xlsx", TipoArquivo.EXTRATO),
        ("Razão SUCESSOR.xlsx", TipoArquivo.RAZAO),
    ]

    for filename, tipo in files_to_test:
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            logger.error(f"Arquivo não encontrado: {path}")
            continue

        importacao = ImportacaoArquivo(
            execucao_id=exec_id,
            nome_original=filename,
            tipo=tipo,
            storage_path=path,
            hash_sha256="fake-hash",
            tamanho_bytes=os.path.getsize(path)
        )
        db.add(importacao)
    db.commit()

    from app.pipeline.runner import SyncRunner
    runner = SyncRunner(None, db)
    runner._execute_pipeline_task(exec_id)

    # Resultados
    logger.info("=== DIAGNÓSTICO DE IMPORTAÇÃO (ARQUIVOS REAIS) ===")
    
    qtd_despesas = db.query(Despesa).filter_by(execucao_id=exec_id).count()
    qtd_parcelas = db.query(ParcelaDespesa).join(Despesa).filter(Despesa.execucao_id==exec_id).count()
    qtd_extrato = db.query(MovimentacaoBancaria).filter_by(execucao_id=exec_id).count()
    qtd_razao = db.query(LancamentoContabil).filter_by(execucao_id=exec_id).count()
    
    logger.info(f"Despesas (Títulos) Importados: {qtd_despesas}")
    logger.info(f"Parcelas Importadas: {qtd_parcelas}")
    logger.info(f"Movimentações Bancárias (Extrato): {qtd_extrato}")
    logger.info(f"Lançamentos Contábeis (Razão): {qtd_razao}")
    
    # Exibir algumas despesas pareadas
    logger.info("\n--- Exemplo de Fornecedores Cadastrados ---")
    for d in db.query(Despesa).filter_by(execucao_id=exec_id).limit(3).all():
        forn = d.fornecedor.nome if d.fornecedor else "N/A"
        logger.info(f"Despesa ID: {d.id_uuid_origem} | Fornecedor: {forn} | Valor: {d.valor_total}")

if __name__ == "__main__":
    verify()
