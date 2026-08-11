import requests
import json
BASE_URL = "http://localhost:8001/api/v1"
auth_data = {"username": "analista@plataformacontabil.com", "password": "analista123"}
response = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
if response.status_code != 200:
    print("Login falhou", response.text)
    exit(1)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

execs = requests.get(f"{BASE_URL}/executions", headers=headers)
print("Executions:", execs.status_code, execs.text)

if execs.status_code == 200 and len(execs.json()) > 0:
    e_id = execs.json()[0]['id']
    summary = requests.get(f"{BASE_URL}/executions/{e_id}/summary", headers=headers)
    print("Summary:", summary.status_code, summary.text)
    
    logs = requests.get(f"{BASE_URL}/executions/{e_id}/logs", headers=headers)
    print("Logs:", logs.status_code, len(logs.json()))
