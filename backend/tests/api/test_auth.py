from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_seed_admin():
    response = client.post("/api/v1/auth/seed-admin")
    # A primeira vez cria os usuários (ou 400 se já existirem)
    assert response.status_code in [200, 400]

def test_login_success():
    client.post("/api/v1/auth/seed-admin")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@contabil.com", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@contabil.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
