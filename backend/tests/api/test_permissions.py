from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_users():
    client.post("/api/v1/auth/seed-admin")
    
    # Tokens
    def get_token(email, pw):
        res = client.post("/api/v1/auth/login", data={"username": email, "password": pw})
        return res.json().get("access_token")
        
    return {
        "admin": get_token("admin@contabil.com", "admin123"),
        "analista": get_token("analista@contabil.com", "analista123"),
        "auditor": get_token("auditor@contabil.com", "auditor123")
    }

def test_auditor_cannot_approve(setup_users):
    auditor_token = setup_users["auditor"]
    # Tenta aprovar candidato fake
    headers = {"Authorization": f"Bearer {auditor_token}"}
    response = client.post(
        "/api/v1/candidates/fake-id/decision",
        json={"action": "APROVAR", "comment": "Aprovado!"},
        headers=headers
    )
    # Auditor deve receber 403 Forbidden
    assert response.status_code == 403

def test_analista_can_run_pipeline(setup_users):
    analista_token = setup_users["analista"]
    headers = {"Authorization": f"Bearer {analista_token}"}
    
    # Tenta criar execução, deve ser permitido (mesmo se o payload tiver faltando, auth passa)
    response = client.post("/api/v1/executions", headers=headers)
    assert response.status_code == 200 # ou 201 se estivesse configurado
    assert "id" in response.json()
