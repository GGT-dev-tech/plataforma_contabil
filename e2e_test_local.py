import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001/api/v1"

def run_e2e_test():
    print("1. Checking API Health...")
    health = requests.get(f"{BASE_URL.replace('/api/v1', '/health')}")
    if health.status_code != 200:
        print("API is not healthy, exiting.")
        sys.exit(1)

    print("\n2. Authenticating as Analista...")
    auth_data = {"username": "analista@plataformacontabil.com", "password": "analista123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n3. Creating Execution...")
    exec_id = requests.post(f"{BASE_URL}/executions", headers=headers).json()["id"]
    
    print("\n4. Uploading files...")
    files = {
        'despesas': open('backend/tests/fixtures/production_sample/Despesas 06-2026.xlsx', 'rb'),
        'razao': open('test_data/real/razao_real.pdf', 'rb'),
        'extrato': open('test_data/real/extrato_real.pdf', 'rb')
    }
    requests.post(f"{BASE_URL}/executions/{exec_id}/files", headers=headers, files=files)

    print("\n5. Running pipeline...")
    requests.post(f"{BASE_URL}/executions/{exec_id}/run", headers=headers)

    print("\n6. Waiting for pipeline to finish...")
    time.sleep(5)

    print("\n7. Fetching Candidates...")
    response = requests.get(f"{BASE_URL}/candidates", headers=headers)
    print(f"Candidates: {len(response.json())}")
    
    # Also fetch the execution status to see if it failed
    # We don't have a GET /executions endpoint, let's query the local DB
    pass

if __name__ == "__main__":
    run_e2e_test()
