import argparse
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.usuario import Usuario
from app.core.security import get_password_hash
from app.models.base import Base

def create_admin_user(email: str, password: str, nome: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        print(f"Usuário {email} já existe.")
        return
        
    novo_usuario = Usuario(
        email=email,
        nome=nome,
        hashed_password=get_password_hash(password),
        is_admin=True,
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
