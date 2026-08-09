import argparse
import uuid
from sqlalchemy.orm import Session
from app.api.deps import SessionLocal, engine
from app.models.domain import Usuario, Role
from app.contexts.identity.auth_utils import get_password_hash
from app.models.base import Base

def create_admin_user(email: str, password: str, nome: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        print(f"Usuário {email} já existe.")
        return
        
    novo_usuario = Usuario(
        id=str(uuid.uuid4()),
        email=email,
        nome=nome,
        hashed_password=get_password_hash(password),
        role=Role.ADMIN,
        is_active=True
    )
    
    db.add(novo_usuario)
    db.commit()
    print(f"Usuário administrador {email} criado com sucesso.")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Admin User")
    parser.add_argument("--email", type=str, required=True, help="Admin Email")
    parser.add_argument("--password", type=str, required=True, help="Admin Password")
    parser.add_argument("--nome", type=str, default="Administrador", help="Admin Name")
    
    args = parser.parse_args()
    create_admin_user(args.email, args.password, args.nome)
