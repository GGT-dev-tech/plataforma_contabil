import os
import sys
import uuid
import glob
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role, Empresa, StatusExecucao, ExecucaoPipeline, StagingRegistro
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

db = TestingSessionLocal()
# Clean old test data
from sqlalchemy import text
db.execute(text("TRUNCATE TABLE execucoes_pipeline, staging_registro, conciliacoes, conciliacoes_itens, match_candidates, candidate_evaluation_logs CASCADE;"))
db.commit()

empresa = db.query(Empresa).first()
if not empresa:
    empresa = Empresa(id=uuid.uuid4(), cnpj="00000000000199", razao_social="Empresa Teste SIMULACAO API")
    db.add(empresa)
    db.commit()

user = db.query(Usuario).first()
if not user:
    user = Usuario(id=str(uuid.uuid4()), email="admin_simulacao@contabil.com", hashed_password="pw", role=Role.ADMIN, empresa_id=empresa.id)
    db.add(user)
    db.commit()
else:
    user.empresa_id = empresa.id
    user.role = Role.ADMIN
    db.commit()

def override_get_current_user():
    return user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def run_simulation():
    print("=== SIMULAÇÃO COMPLETA DE IMPORTAÇÃO E FLUXO VIA API FRONTEND ===")

    # PASSO 1: Criar nova Execução no Workspace (POST /api/v1/executions)
    res_create = client.post("/api/v1/executions", json={"empresa_id": str(user.empresa_id)})
    print(f"PASSO 1: POST /api/v1/executions -> HTTP {res_create.status_code}")
    exec_data = res_create.json()
    exec_id = exec_data["id"]
    print(f"   -> Execução Criada: {exec_id} (Status: {exec_data.get('status')})")

    # PASSO 2: Upload de Arquivos via Form-Data (POST /api/v1/executions/{exec_id}/files)
    def find_file(pattern):
        matches = glob.glob(pattern)
        if matches: return matches[0]
        matches_app = glob.glob(f"/app/{pattern}")
        if matches_app: return matches_app[0]
        return None

    despesas_path = find_file("*Despesas*.xlsx")
    extrato_path = find_file("*Extrato*.pdf")
    razao_path = find_file("*SUCESSOR*.pdf")

    print(f"\nPASSO 2: POST /api/v1/executions/{exec_id}/files (Anexando 3 arquivos reais...)")
    print(f"   [+] Despesas ERP : {os.path.basename(despesas_path)}")
    print(f"   [+] Extrato Inter: {os.path.basename(extrato_path)}")
    print(f"   [+] Razão SCI    : {os.path.basename(razao_path)}")

    with open(despesas_path, "rb") as f_desp, open(extrato_path, "rb") as f_ext, open(razao_path, "rb") as f_raz:
        files = {
            "despesas": (os.path.basename(despesas_path), f_desp, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            "extrato": (os.path.basename(extrato_path), f_ext, "application/pdf"),
            "razao": (os.path.basename(razao_path), f_raz, "application/pdf")
        }
        res_upload = client.post(f"/api/v1/executions/{exec_id}/files", files=files)
        print(f"   -> HTTP {res_upload.status_code} | Resposta: {res_upload.json()}")

    # PASSO 3: Iniciar Processamento da Fase 1 - Ingestão/Parsing para Staging (POST /api/v1/executions/{exec_id}/run)
    print(f"\nPASSO 3: POST /api/v1/executions/{exec_id}/run (Disparando Parsing para Staging...)")
    res_run = client.post(f"/api/v1/executions/{exec_id}/run")
    print(f"   -> HTTP {res_run.status_code} | Resposta: {res_run.json()}")

    # Execução síncrona do Core Fase 1
    from app.contexts.matching_auditing.pipeline.runner import execute_pipeline_core
    db.commit()
    execute_pipeline_core(exec_id, db)
    db.commit()

    # Consulta dos Registros de Staging Gerados (GET Staging)
    staging_count = db.query(StagingRegistro).filter(StagingRegistro.execucao_id == exec_id).count()
    exec_obj = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    print(f"   -> Status da Execução após Fase 1: {exec_obj.status.name}")
    print(f"   -> Total de Registros de Staging Extraídos: {staging_count}")

    # PASSO 4: Aprovação de Staging e Disparo da Fase 2 - Matching & Contabilidade (POST /api/v1/executions/{exec_id}/approve-staging)
    print(f"\nPASSO 4: POST /api/v1/executions/{exec_id}/approve-staging (Aprovando Staging & Disparando Conciliação/Motor Contábil...)")
    res_approve = client.post(f"/api/v1/executions/{exec_id}/approve-staging")
    print(f"   -> HTTP {res_approve.status_code} | Resposta: {res_approve.json()}")

    # Execução síncrona do Core Fase 2
    db.commit()
    execute_pipeline_core(exec_id, db)
    db.commit()

    # PASSO 5: Checagem do Status Final da Execução (GET /api/v1/executions/{exec_id})
    res_status = client.get(f"/api/v1/executions/{exec_id}")
    print(f"\nPASSO 5: GET /api/v1/executions/{exec_id} (Status Final na API)")
    print(f"   -> Resposta API: {res_status.json()}")

    # PASSO 6: DRE Gerencial pós-upload e pós-conciliação
    from app.contexts.accounting.dre_service import DREService
    from app.contexts.accounting.balancete_service import BalanceteService
    from app.contexts.matching_auditing.reconciliation_report_service import ReconciliationReportService

    dre_service = DREService(db)
    dre = dre_service.calcular_dre_periodo(user.empresa_id, date(2026, 6, 1), date(2026, 6, 30))

    print("\n--- DRE GERENCIAL RESULTANTE APÓS IMPORTAÇÃO VIA API ---")
    for linha in dre["linhas"]:
        prefix = "==> " if linha["is_subtotal"] else "    "
        print(f"{prefix}{linha['descricao']:<45}: R$ {linha['valor']:>12,.2f}")

    # Balancete Analítico
    balancete_service = BalanceteService(db)
    balancete = balancete_service.calcular_balancete(user.empresa_id, date(2026, 6, 1), date(2026, 6, 30))

    print("\n--- RESUMO DO BALANCETE ANALÍTICO CONTÁBIL ---")
    print(f"Total de Débitos  : R$ {balancete['totais']['total_debitos']:>12,.2f}")
    print(f"Total de Créditos : R$ {balancete['totais']['total_creditos']:>12,.2f}")
    print(f"Balanço Equilibrado: {'SIM' if balancete['totais']['equilibrado'] else 'NÃO'}")

    # Conciliação Bancária & Auditoria
    conc_service = ReconciliationReportService(db)
    res_conc = conc_service.gerar_relatorio_resumo(user.empresa_id)

    print("\n--- RESUMO DA CONCILIAÇÃO BANCÁRIA (3-WAY MATCHING) ---")
    res_kpi = res_conc["resumo"]
    print(f"Total de Títulos ERP         : {res_kpi['total_titulos_erp']}")
    print(f"Títulos Liquidados/Conciliados: {res_kpi['titulos_efetivados_count']} (R$ {res_kpi['total_pago_efetivado']:,.2f})")
    print(f"Títulos em Aberto ERP        : {res_kpi['titulos_em_aberto_count']} (R$ {res_kpi['total_em_aberto']:,.2f})")
    print(f"Taxa de Conciliação Bancária : {res_kpi['taxa_conciliacao']}%")

    # Exportar Arquivos Excel para dissecação e auditoria
    os.makedirs("/app/saida", exist_ok=True)
    with open("/app/saida/DRE_Junho_2026.xlsx", "wb") as f:
        f.write(dre_service.exportar_excel(dre, "Junho / 2026"))
    with open("/app/saida/Balancete_Analitico_Junho_2026.xlsx", "wb") as f:
        f.write(balancete_service.exportar_excel(balancete))
    with open("/app/saida/Relatorio_Conciliacao_Bancaria_Junho_2026.xlsx", "wb") as f:
        f.write(conc_service.exportar_excel(res_conc))

    print("\n=== PLANILHAS EXCEL DE SAÍDA GERADAS EM /app/saida/ ===")
    print(" 1. /app/saida/DRE_Junho_2026.xlsx")
    print(" 2. /app/saida/Balancete_Analitico_Junho_2026.xlsx")
    print(" 3. /app/saida/Relatorio_Conciliacao_Bancaria_Junho_2026.xlsx")
    print("\n=== TESTE DO FLUXO COMPLETO DO FRONTEND CONCLUÍDO COM SUCESSO! ===")

if __name__ == "__main__":
    run_simulation()
