import requests
import json
import time
import sys

BASE_URL = "https://backend-production-8502.up.railway.app/api/v1"

def run_e2e_test():
    print("1. Checking API Health...")
    health = requests.get(f"https://backend-production-8502.up.railway.app/health")
    print(f"Health check status: {health.status_code}")
    if health.status_code != 200:
        print("API is not healthy, exiting.")
        sys.exit(1)

    print("\n2. Authenticating as Analista...")
    auth_data = {
        "username": "analista@plataformacontabil.com",
        "password": "analista123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
    if response.status_code != 200:
        print(f"Auth failed: {response.status_code} {response.text}")
        sys.exit(1)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Authenticated successfully.")

    print("\n3. Creating Execution...")
    response = requests.post(f"{BASE_URL}/executions", headers=headers)
    if response.status_code != 200:
        print(f"Execution creation failed: {response.status_code} {response.text}")
        sys.exit(1)
    
    exec_id = response.json()["id"]
    print(f"Execution created with ID: {exec_id}")

    print("\n4. Uploading files...")
    files = {
        'despesas': open('test_data/despesas_sample.csv', 'rb'),
        'razao': open('test_data/razao_sample.csv', 'rb'),
        'extrato': open('test_data/extrato_sample.csv', 'rb')
    }
    response = requests.post(f"{BASE_URL}/executions/{exec_id}/files", headers=headers, files=files)
    if response.status_code != 202:
        print(f"File upload failed: {response.status_code} {response.text}")
        sys.exit(1)
    print("Files uploaded successfully.")

    print("\n5. Running pipeline...")
    response = requests.post(f"{BASE_URL}/executions/{exec_id}/run", headers=headers)
    if response.status_code != 202:
        print(f"Pipeline run failed: {response.status_code} {response.text}")
        sys.exit(1)
    print("Pipeline started.")

    print("\n6. Waiting for pipeline to finish...")
    time.sleep(5)  # Wait for background task to finish

    print("\n7. Fetching Candidates...")
    response = requests.get(f"{BASE_URL}/candidates", headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch candidates: {response.status_code} {response.text}")
        sys.exit(1)
    
    candidates = response.json()
    print(f"Found {len(candidates)} candidates.")
    
    with open('test_data/e2e_results.json', 'w') as f:
        json.dump(candidates, f, indent=2)
    print("Saved candidates to test_data/e2e_results.json")
    
    print("\nE2E Test Completed Successfully!")

if __name__ == "__main__":
    run_e2e_test()
