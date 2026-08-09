import sys
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import engine
from sqlalchemy.orm import Session
from app.models.domain import Usuario
from app.contexts.identity.auth_utils import get_password_hash

# Force the admin user to have the right password locally
with Session(engine) as db:
    admin = db.query(Usuario).filter(Usuario.email == "admin@plataformacontabil.com").first()
    if admin:
        admin.hashed_password = get_password_hash("admin123")
        db.commit()

client = TestClient(app)
response = client.post("/api/v1/auth/login", data={"username": "admin@plataformacontabil.com", "password": "admin123"})
print(response.status_code)
print(response.json())
