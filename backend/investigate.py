import os
import sys
import pandas as pd
from io import BytesIO
import json
import uuid

# Configurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.deps import SessionLocal
from app.models.domain import (
    ExecucaoPipeline, StatusExecucao, ImportacaoArquivo, TipoArquivo,
    MovimentacaoBancaria, Despesa, ParcelaDespesa, Fornecedor,
    LancamentoContabil, MatchCandidate, ConciliacaoItem
)
from app.services.storage import LocalStorageProvider
from app.pipeline.runner import SyncRunner
from fastapi import BackgroundTasks

def main():
    print("=== INICIANDO SPRINT DE CONFIABILIDADE DA IMPORTAÇÃO ===")
    
    # 1. Converter CSV para XLSX para testar o formato Excel real
    print("\n--- ETAPA 0: GERANDO ARQUIVOS .XLSX DE TESTE ---")
    data_dir = "test_data"
    
    for f in ["despesas_sample", "extrato_sample", "razao_sample"]:
        csv_path = os.path.join(data_dir, f + ".csv")
        xlsx_path = os.path.join(data_dir, f + ".xlsx")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_excel(xlsx_path, index=False)
            print(f"Gerado {xlsx_path} a partir de {csv_path}")

    # Inicializar banco
    db = SessionLocal()
    
    try:
        # 1. Upload do Arquivo
        print("\n--- ETAPA 1: UPLOAD DO ARQUIVO ---")
        execucao_id = str(uuid.uuid4())
        execucao = ExecucaoPipeline(
            id=execucao_id,
            status=StatusExecucao.ARQUIVOS_ANEXADOS,
            matching_profile="financeiro_2026",
            runtime_profile="api"
        )
        db.add(execucao)
        
        storage = LocalStorageProvider(base_dir="uploads/test_investigation")
        hashes = {}
        
        for f, tipo in [("despesas_sample.csv", TipoArquivo.DESPESA), 
                        ("extrato_sample.csv", TipoArquivo.EXTRATO), 
                        ("razao_sample.csv", TipoArquivo.RAZAO)]:
            path = os.path.join(data_dir, f)
            if not os.path.exists(path):
                continue
                
            with open(path, "rb") as file_stream:
                content = file_stream.read()
                file_stream.seek(0)
                import hashlib
                sha256 = hashlib.sha256(content).hexdigest()
                tamanho = len(content)
                
                # mock FastAPI UploadFile behavior
                storage_path = storage.save(execucao_id, f, file_stream)
                
                arquivo = ImportacaoArquivo(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    nome_original=f,
                    tipo=tipo,
                    storage_path=storage_path,
                    hash_sha256=sha256,
                    tamanho_bytes=tamanho,
                    uploaded_by="investigacao"
                )
                db.add(arquivo)
                hashes[tipo.value] = f
                
                print(f"Arquivo recebido: {f}")
                print(f"  Tamanho: {tamanho} bytes")
                print(f"  Hash: {sha256}")
                print(f"  Path armazenado: {storage_path}")

        execucao.hashes_arquivos = json.dumps(hashes)
        db.commit()
        
        # 2 e 3 e 4. Rodar o Parser e Persistência
        print("\n--- ETAPA 2 e 3: LEITURA EXCEL E PARSER ---")
        print("Executando pipeline que faz o parser dos arquivos...")
        
        class FakeBackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                func(*args, **kwargs)
                
        bg_tasks = FakeBackgroundTasks()
        runner = SyncRunner(bg_tasks, db)
        runner.run(execucao_id)
        
        db.commit()
        
        print("\n--- ETAPA 4: PERSISTÊNCIA NO MODELO CANÔNICO ---")
        # Verificar o que foi pro banco
        movs = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.execucao_id == execucao_id).all()
        despesas = db.query(Despesa).filter(Despesa.execucao_id == execucao_id).all()
        parcelas = db.query(ParcelaDespesa).join(Despesa).filter(Despesa.execucao_id == execucao_id).all()
        fornecedores = db.query(Fornecedor).all()
        
        print(f"Movimentacoes importadas: {len(movs)}")
        for i, m in enumerate(movs):
            print(f"  Mov {i+1}: ID={m.id}, Histórico='{m.historico}', Valor={m.valor}, Data={m.data}")
            
        print(f"\nDespesas importadas: {len(despesas)}")
        print(f"Parcelas importadas: {len(parcelas)}")
        for i, p in enumerate(parcelas):
            print(f"  Par {i+1}: ID={p.id}, Valor={p.valor}, Venc={p.data_vencimento}, Doc={p.id_parcela_origem}")

        print("\n--- ETAPA 5: ENGINE DE CONCILIAÇÃO ---")
        candidates = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == execucao_id).all()
        print(f"Candidatos gerados: {len(candidates)}")
        for c in candidates:
            print(f"  Candidato ID={c.id}, Status={c.status}, Score={c.score_total}")
            
        # Comparar com o arquivo original para mostrar perdas
        print("\n--- DIAGNÓSTICO DE PERDAS ---")
        df_ext = pd.read_csv(os.path.join(data_dir, "extrato_sample.csv"))
        df_desp = pd.read_csv(os.path.join(data_dir, "despesas_sample.csv"))
        print(f"Linhas no arquivo extrato original: {len(df_ext)}")
        print(f"Movimentacoes no banco: {len(movs)}")
        print(f"Perda extrato: {len(df_ext) - len(movs)}")
        print(f"Linhas no arquivo despesas original: {len(df_desp)}")
        print(f"Parcelas no banco: {len(parcelas)}")
        print(f"Perda despesas/parcelas: {len(df_desp) - len(parcelas)}")
        
        print("\n=== INVESTIGAÇÃO CONCLUÍDA ===")

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
