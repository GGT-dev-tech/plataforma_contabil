import os
import uuid
import json
import hashlib
from datetime import date
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.domain import (
    Empresa, Usuario, Role, ExecucaoPipeline, StatusExecucao,
    ImportacaoArquivo, TipoArquivo, StagingRegistro, TipoStaging, Conciliacao
)
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro, ConciliacaoFinanceira
from app.models.ledger import PartidaItem, LancamentoCabecalho
from app.services.storage import LocalStorageProvider
from app.contexts.matching_auditing.pipeline.runner import execute_pipeline_core
from app.contexts.accounting.dre_service import DREService

def run_test():
    db: Session = next(get_db())
    print("=== INICIANDO TESTE DO FLUXO DE CONCILIAÇÃO & INGESTÃO ===", flush=True)

    # 1. Criar Workspace Isolado Único para o Teste
    empresa_id = str(uuid.uuid4())
    empresa = Empresa(
        id=empresa_id,
        cnpj=f"59.120.530/{uuid.uuid4().hex[:4]}",
        razao_social="Vnp - Spe Empreendimentos Imobiliarios Ltda",
        nome_fantasia="VNP SPE"
    )
    db.add(empresa)
    db.commit()
    print(f"-> Workspace Ativo: {empresa.nome_fantasia} (ID: {empresa.id})", flush=True)

    # 2. Garantir Usuário
    usuario = db.query(Usuario).first()
    if not usuario:
        usuario = Usuario(
            id=str(uuid.uuid4()),
            email="admin@contabil.com",
            hashed_password="hash",
            role=Role.ADMIN,
            empresa_id=empresa.id
        )
        db.add(usuario)
        db.commit()

    # 3. Criar ExecucaoPipeline
    exec_id = str(uuid.uuid4())
    execucao = ExecucaoPipeline(
        id=exec_id,
        empresa_id=empresa.id,
        status=StatusExecucao.CRIADA,
        matching_profile="financeiro_2026",
        runtime_profile="api"
    )
    db.add(execucao)
    db.commit()
    print(f"-> Execução de Pipeline Criada: {exec_id}", flush=True)

    # 4. Anexar Arquivos da Raiz do Projeto
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root_dir, "Despesas 06-2026.xlsx")):
        root_dir = "/Users/gustavo/Documents/dev/projects/plataforma_contabil"
        
    arquivos_alvo = [
        ("Despesas 06-2026.xlsx", TipoArquivo.DESPESA, "despesas"),
        ("Extrato-01-06-2026-a-30-06-2026-PDF.pdf", TipoArquivo.EXTRATO, "extrato"),
        ("Razão SUCESSOR.pdf", TipoArquivo.RAZAO, "razao"),
    ]

    storage = LocalStorageProvider()
    hashes = {}

    for fname, tipo, key in arquivos_alvo:
        fpath = os.path.join(root_dir, fname)
        if not os.path.exists(fpath):
            print(f"⚠️ Arquivo não encontrado na raiz: {fname}", flush=True)
            continue

        with open(fpath, "rb") as f:
            content = f.read()
            sha256 = hashlib.sha256(content).hexdigest()
            tamanho = len(content)

        with open(fpath, "rb") as f:
            saved_path = storage.save(exec_id, fname, f)

        imp = ImportacaoArquivo(
            id=str(uuid.uuid4()),
            execucao_id=exec_id,
            nome_original=fname,
            tipo=tipo,
            storage_path=saved_path,
            hash_sha256=sha256,
            tamanho_bytes=tamanho,
            uploaded_by=usuario.id
        )
        db.add(imp)
        hashes[key] = fname
        print(f"  [+] Anexado: {fname} ({tamanho / 1024:.1f} KB)", flush=True)

    execucao.status = StatusExecucao.ARQUIVOS_ANEXADOS
    execucao.hashes_arquivos = json.dumps(hashes)
    db.commit()

    # 5. Executar FASE 1: Ingestão e Parsing para Staging
    print("\n--- INICIANDO FASE 1: INGESTÃO E PARSING (STAGING) ---", flush=True)
    execucao.status = StatusExecucao.PROCESSANDO
    db.commit()

    execute_pipeline_core(exec_id, db)

    # Verificar Staging
    staging_records = db.query(StagingRegistro).filter(StagingRegistro.execucao_id == exec_id).all()
    print(f"✅ Total de Registros de Staging Criados: {len(staging_records)}", flush=True)
    
    extratos_stg = [s for s in staging_records if s.tipo == TipoStaging.EXTRATO]
    despesas_stg = [s for s in staging_records if s.tipo == TipoStaging.DESPESA]
    
    print(f"   - Registros de Extrato/Razão: {len(extratos_stg)}", flush=True)
    print(f"   - Registros de Despesas ERP: {len(despesas_stg)}", flush=True)

    if len(staging_records) > 0:
        print("\nExemplo dos primeiros registros de Staging extraídos:", flush=True)
        for stg in staging_records[:5]:
            print(f"   • [{stg.data}] {stg.tipo.name} | {stg.descricao[:45]} | R$ {stg.valor:.2f}", flush=True)

    # 6. Aprovar Staging e Executar FASE 2: Conciliação, Matching & Motor Contábil
    print("\n--- INICIANDO FASE 2: CONCILIAÇÃO (MATCHING & MOTOR CONTÁBIL) ---", flush=True)
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    execucao.status = StatusExecucao.CONCILIANDO
    db.commit()

    execute_pipeline_core(exec_id, db)

    # 7. Resultados Finais
    execucao = db.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
    print(f"\n================ RESULTADOS DA EXECUÇÃO ================", flush=True)
    print(f"Status Final da Execução: {execucao.status.name}", flush=True)

    if execucao.status == StatusExecucao.ERRO:
        print(f"❌ Código de Erro: {execucao.erro_codigo}", flush=True)
        print(f"❌ Mensagem: {execucao.erro_mensagem}", flush=True)
        print(f"❌ Stacktrace: {execucao.erro_stacktrace}", flush=True)
        return

    # Verificar Movimentações e Títulos Criados
    movs = db.query(MovimentacaoFinanceira).filter(MovimentacaoFinanceira.empresa_id == empresa.id).all()
    titulos = db.query(TituloFinanceiro).filter(TituloFinanceiro.empresa_id == empresa.id).all()
    conciliacoes = db.query(ConciliacaoFinanceira).filter(ConciliacaoFinanceira.empresa_id == empresa.id).all()
    partidas = db.query(LancamentoCabecalho).filter(LancamentoCabecalho.empresa_id == empresa.id).all()

    print(f"-> Movimentações Financeiras Registradas: {len(movs)}", flush=True)
    print(f"-> Títulos Financeiros Registrados: {len(titulos)}", flush=True)
    print(f"-> Conciliações Efetuadas: {len(conciliacoes)}", flush=True)
    print(f"-> Lançamentos Contábeis (Partidas Dobradas): {len(partidas)}", flush=True)

    # 8. Calcular DRE Resultante
    dre_service = DREService(db)
    dre_resultado = dre_service.calcular_dre_periodo(empresa.id, date(2026, 6, 1), date(2026, 6, 30))
    print("\n--- DRE GERENCIAL RESULTANTE (JUNHO / 2026) ---", flush=True)
    if isinstance(dre_resultado, dict) and "linhas" in dre_resultado:
        for linha in dre_resultado["linhas"]:
            is_sub = linha.get("is_subtotal", False)
            prefix = "==>" if is_sub else "   "
            print(f"{prefix} {linha['descricao']:45s}: R$ {linha['valor']:>14,.2f}", flush=True)
    elif isinstance(dre_resultado, dict):
        for k, v in dre_resultado.items():
            print(f"   {str(k):35s}: {v}", flush=True)
    else:
        print(dre_resultado, flush=True)

    print("\n=== TESTE DA FERRAMENTA DE CONCILIAÇÃO CONCLUÍDO COM SUCESSO! ===", flush=True)

if __name__ == "__main__":
    run_test()
