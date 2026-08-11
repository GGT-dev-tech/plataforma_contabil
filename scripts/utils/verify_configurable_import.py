import os
import requests
import json
import time

API_URL = "http://localhost:8001/api/v1"

# 1. Obter o admin token
resp = requests.post(f"{API_URL}/auth/login", json={"email": "admin@plataforma.com", "password": "admin"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Configurar a Empresa (Workspace) com o import_config
# Vamos pegar a empresa do admin
me_resp = requests.get(f"{API_URL}/auth/me", headers=headers)
me = me_resp.json()
empresa_id = me["empresa_id"]

# Como não temos uma rota para atualizar a empresa, vamos fazer via BD
import psycopg2
conn = psycopg2.connect("dbname=contabil user=postgres password=postgres host=localhost port=5432")
cur = conn.cursor()
import_config = {
    "DESPESA": {
        "col_data": "Vencimento Parcela",
        "col_valor": "Valor Parcela",
        "col_descricao": "ID Parcela",
        "col_entidade": "Fornecedor",
        "skip_rows": 0
    }
}
cur.execute("UPDATE empresas SET import_config = %s WHERE id = %s", (json.dumps(import_config), empresa_id))
conn.commit()
cur.close()
conn.close()

# 3. Criar Execução
exec_resp = requests.post(f"{API_URL}/executions", headers=headers, json={"empresa_id": empresa_id})
exec_id = exec_resp.json()["id"]
print(f"Execucao criada: {exec_id}")

# 4. Enviar arquivos
files = {
    "despesas": open("backend/tests/fixtures/production_sample/Despesas 06-2026.xlsx", "rb")
}
requests.post(f"{API_URL}/executions/{exec_id}/files", headers=headers, files=files)

# 5. Iniciar Pipeline
requests.post(f"{API_URL}/executions/{exec_id}/run", headers=headers)

# 6. Aguardar
print("Aguardando pipeline...")
time.sleep(5)

# 7. Checar Status
summary_resp = requests.get(f"{API_URL}/executions/{exec_id}/summary", headers=headers)
print(json.dumps(summary_resp.json(), indent=2))
