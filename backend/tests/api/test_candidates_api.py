from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    client.post("/api/v1/auth/seed-admin")
    res = client.post("/api/v1/auth/login", data={"username": "admin@contabil.com", "password": "admin123"})
    return res.json().get("access_token")

def test_list_candidates(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/candidates", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_decision_candidate_not_found(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post(
        "/api/v1/candidates/invalid-uuid/decision", 
        json={"action": "APROVAR"},
        headers=headers
    )
    assert res.status_code == 404

def test_list_divergencies(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/divergencies", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
