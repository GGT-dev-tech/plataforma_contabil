import requests
import json

BASE_URL = "https://backend-production-8502.up.railway.app/api/v1"

auth_data = {"username": "analista@plataformacontabil.com", "password": "analista123"}
token = requests.post(f"{BASE_URL}/auth/login", data=auth_data).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# List last executions
response = requests.get(f"{BASE_URL}/executions", headers=headers)
execs = response.json()
print("Executions:")
print(json.dumps(execs, indent=2))
