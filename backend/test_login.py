import sys
import os
from sqlalchemy.orm import Session
from app.api.deps import engine
from app.models.domain import Usuario
from app.contexts.identity.auth_utils import verify_password

def test():
    with Session(engine) as db:
        user = db.query(Usuario).filter(Usuario.email == "admin@plataformacontabil.com").first()
        if not user:
            print("USER NOT FOUND")
            return
        
        print(f"Hash in DB: {user.hashed_password}")
        
        is_valid = verify_password("admin123", user.hashed_password)
        print(f"Valid: {is_valid}")

if __name__ == '__main__':
    test()
