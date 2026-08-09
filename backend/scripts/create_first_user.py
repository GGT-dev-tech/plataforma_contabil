import sys
import os

# Add the parent directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.api.deps import engine
from app.models.domain import Usuario, Role
from app.contexts.identity.auth_utils import get_password_hash

def create_initial_users():
    print("Creating initial users...")
    with Session(engine) as db:
        # Check if users already exist
        admin = db.query(Usuario).filter(Usuario.email == "admin@plataformacontabil.com").first()
        if admin:
            print("Admin user exists. Forcefully resetting password to ensure hash compatibility...")
            admin.hashed_password = get_password_hash("admin123")
            db.commit()
            print("Admin password reset.")
            return

        # Create Admin
        admin_user = Usuario(
            email="admin@plataformacontabil.com",
            nome="Administrador",
            hashed_password=get_password_hash("admin123"),
            role=Role.ADMIN,
            is_active=True
        )

        # Create Analyst
        analista_user = Usuario(
            email="analista@plataformacontabil.com",
            nome="Analista Contábil",
            hashed_password=get_password_hash("analista123"),
            role=Role.ANALISTA,
            is_active=True
        )
        
        # Create Auditor
        auditor_user = Usuario(
            email="auditor@plataformacontabil.com",
            nome="Auditor Chefe",
            hashed_password=get_password_hash("auditor123"),
            role=Role.AUDITOR,
            is_active=True
        )

        db.add(admin_user)
        db.add(analista_user)
        db.add(auditor_user)
        
        db.commit()
        print("Initial users created successfully!")
        print("Credentials:")
        print(" - admin@plataformacontabil.com / admin123")
        print(" - analista@plataformacontabil.com / analista123")
        print(" - auditor@plataformacontabil.com / auditor123")
        print("\nPlease change passwords immediately after login.")

if __name__ == "__main__":
    create_initial_users()
