import os
import time
import json
import csv
import logging
import shutil
import uuid
from decimal import Decimal
from datetime import datetime
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.domain import TipoArquivo, MovimentacaoBancaria, ParcelaDespesa, Fornecedor, ConciliacaoExplicacao
from app.parsers.excel.despesas_parser import ExcelDespesasParser
from app.parsers.excel.razao_sci_parser import SciRazaoParser
from app.parsers.excel.extrato_inter_parser import ExtratoInterParser
from app.services.enrichment import EnrichmentService
from app.engine.core import MatchOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("E2E_Pipeline")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def generate_csv(filepath, data, fieldnames):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def generate_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)

def main():
    logger.info("Iniciando Plataforma de Conciliação End-to-End...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = f"reports/{timestamp}"
    os.makedirs(report_dir, exist_ok=True)
    db_path = f"{report_dir}/database_snapshot.sqlite"
    
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    start_time = time.time()
    
    path_despesas = "tests/fixtures/production_sample/Despesas 06-2026.xlsx"
    path_sci = "tests/fixtures/production_sample/Razão SUCESSOR.xlsx"
    path_inter = "tests/fixtures/production_sample/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
    
    # Valida caminhos ou usa fallback
    if not os.path.exists(path_despesas):
        path_despesas = "../Despesas 06-2026.xlsx"
        path_sci = "../Razão SUCESSOR.xlsx"
        path_inter = "../Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
        
    p_despesas = ExcelDespesasParser()
    rep_despesas = p_despesas.execute(path_despesas, TipoArquivo.DESPESA, db, action_if_exists="BLOCK")
    
    p_sci = SciRazaoParser()
    rep_sci = p_sci.execute(path_sci, TipoArquivo.RAZAO, db, action_if_exists="BLOCK")
    
    p_inter = ExtratoInterParser()
    rep_inter = p_inter.execute(path_inter, TipoArquivo.EXTRATO, db, action_if_exists="BLOCK")
    
    t_enrich_start = time.time()
    movimentacoes = db.query(MovimentacaoBancaria).all()
    parcelas = db.query(ParcelaDespesa).all()
    fornecedores = {f.id: f for f in db.query(Fornecedor).all()}
    
    EnrichmentService.enrich_movimentacoes(movimentacoes)
    EnrichmentService.enrich_parcelas(parcelas, fornecedores)
    
    orchestrator = MatchOrchestrator(db)
    stats = orchestrator.run_pipeline()
    
    total_time = time.time() - start_time
    
    # ==========================
    # GERACAO DOS ARTEFATOS
    # ==========================
    
    # Validação do Snapshot
    with engine.connect() as conn:
        from sqlalchemy import text
        db_summary = {
            "conciliacoes": conn.execute(text("SELECT COUNT(*) FROM conciliacoes")).scalar(),
            "conciliacoes_itens": conn.execute(text("SELECT COUNT(*) FROM conciliacoes_itens")).scalar(),
            "conciliacao_explicacoes": conn.execute(text("SELECT COUNT(*) FROM conciliacao_explicacoes")).scalar(),
            "movimentacoes_bancarias": conn.execute(text("SELECT COUNT(*) FROM movimentacoes_bancarias")).scalar(),
            "parcelas_despesa": conn.execute(text("SELECT COUNT(*) FROM parcelas_despesa")).scalar()
        }
    generate_json(f"{report_dir}/database_summary.json", db_summary)
    
    import hashlib
    def get_file_hash(filepath):
        h = hashlib.sha256()
        with open(filepath, 'rb') as file:
            while chunk := file.read(8192):
                h.update(chunk)
        return h.hexdigest()

    import platform
    hashes = {
        "despesas": get_file_hash(path_despesas),
        "razao": get_file_hash(path_sci),
        "extrato": get_file_hash(path_inter)
    }
    
    # Atualiza a ExecucaoPipeline com os hashes (E2E simulation)
    execucao = orchestrator.execucao
    execucao.hashes_arquivos = json.dumps(hashes)
    db.commit()

    manifest = {
        "execution_id": str(execucao.id),
        "python_version": platform.python_version(),
        "matching_profile": orchestrator.profile['matching_profile'],
        "runtime_profile": "production",
        "started_at": execucao.data_inicio.isoformat(),
        "finished_at": execucao.data_fim.isoformat() if execucao.data_fim else datetime.now().isoformat(),
        "duration_ms": execucao.duracao_ms,
        "input_files": hashes
    }
    generate_json(f"{report_dir}/manifest.json", manifest)

    # 1. Technical Metrics
    technical = {
        "execution_time_seconds": total_time,
        "despesas_linhas_lidas": rep_despesas.metrics.linhas_lidas,
        "despesas_linhas_validas": rep_despesas.metrics.linhas_validas,
        "inter_linhas_lidas": rep_inter.metrics.linhas_lidas,
        "inter_linhas_validas": rep_inter.metrics.linhas_validas,
        "sci_linhas_lidas": rep_sci.metrics.linhas_lidas,
        "sci_linhas_validas": rep_sci.metrics.linhas_validas,
        "candidate_generator": orchestrator.candidate_gen.metrics
    }
    generate_json(f"{report_dir}/technical_metrics.json", technical)
    
    # 2. Business Metrics
    business = stats
    generate_json(f"{report_dir}/business_metrics.json", business)
    
    # 3. Explainability JSON
    explicacoes = db.query(ConciliacaoExplicacao).all()
    exp_data = [{"conciliacao_id": str(e.conciliacao_id), "regra": e.regra, "score": e.score, "peso": e.peso, "justificativa": e.justificativa} for e in explicacoes]
    generate_json(f"{report_dir}/explainability.json", exp_data)
    
    # 4. Reconciliation JSON
    generate_json(f"{report_dir}/reconciliation.json", orchestrator.reconciliation_log)
    
    # 5. CSVs
    if orchestrator.reconciliation_log:
        generate_csv(f"{report_dir}/reconciliation.csv", orchestrator.reconciliation_log, orchestrator.reconciliation_log[0].keys())
        
    all_discards = orchestrator.candidate_gen.discard_log + orchestrator.candidates_discard_engine_log
    if all_discards:
        keys = ["mov_id", "parcela_id", "motivo", "score"]
        data = []
        for d in all_discards:
            data.append({"mov_id": d.get("mov_id"), "parcela_id": d.get("parcela_id"), "motivo": d.get("motivo"), "score": d.get("score", "")})
        generate_csv(f"{report_dir}/candidates.csv", data, keys)
        
    if orchestrator.divergencias_log:
        generate_csv(f"{report_dir}/divergencias.csv", orchestrator.divergencias_log, orchestrator.divergencias_log[0].keys())
        
    # 6. Rule Statistics CSV
    stats_data = []
    for rule_name, stat in orchestrator.scoring.rule_stats.items():
        executada = stat["executada"]
        avg_time = stat["tempo_total_ms"] / executada if executada > 0 else 0
        avg_score = stat["score_total"] / executada if executada > 0 else 0
        
        stats_data.append({
            "Regra": rule_name, 
            "Execucoes": executada, 
            "Aprovou": stat["aprovou"], 
            "Rejeitou": stat["rejeitou"], 
            "Tempo Medio (ms)": f"{avg_time:.4f}",
            "Score Medio": f"{avg_score:.2f}"
        })
    if stats_data:
        generate_csv(f"{report_dir}/rule_statistics.csv", stats_data, ["Regra", "Execucoes", "Aprovou", "Rejeitou", "Tempo Medio (ms)", "Score Medio"])

    logger.info(f"Pipeline executada com sucesso. Relatórios e Snapshot gerados em: {report_dir}")

if __name__ == "__main__":
    main()
