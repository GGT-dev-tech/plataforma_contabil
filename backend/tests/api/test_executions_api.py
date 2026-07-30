from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    client.post("/api/v1/auth/seed-admin")
    res = client.post("/api/v1/auth/login", data={"username": "admin@contabil.com", "password": "admin123"})
    return res.json().get("access_token")

def test_create_and_upload(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create Execution
    res = client.post("/api/v1/executions", headers=headers)
    assert res.status_code == 200
    exec_id = res.json()["id"]
    
    # 2. Upload Files (mock form-data)
    # We just create dummy files to send
    files = {
        'despesas': ('desp.csv', b'foo,bar\n1,2'),
        'razao': ('razao.csv', b'foo,bar\n1,2'),
        'extrato': ('extrato.csv', b'foo,bar\n1,2'),
    }
    res2 = client.post(f"/api/v1/executions/{exec_id}/files", files=files, headers=headers)
    assert res2.status_code == 202
    
    # 3. Run Pipeline
    res3 = client.post(f"/api/v1/executions/{exec_id}/run", headers=headers)
    assert res3.status_code == 202
    assert res3.json()["status"] == "PROCESSING"
