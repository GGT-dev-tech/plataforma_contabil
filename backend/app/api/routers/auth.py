import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth import create_access_token, verify_password, get_password_hash
from app.models.domain import Usuario, Role
from app.core.config import settings
from app.core.uow import SQLAlchemyUnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "nome": user.nome,
        "role": user.role.value
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    if settings.APP_ENV == "production":
        raise HTTPException(status_code=403, detail="Endpoint desabilitado em ambiente de produção.")
    
    with SQLAlchemyUnitOfWork(db) as uow:
        if uow.session.query(Usuario).first():
            raise HTTPException(status_code=400, detail="Banco já populado")
        admin = Usuario(id=str(uuid.uuid4()), email="admin@contabil.com", hashed_password=get_password_hash("admin123"), nome="Administrador", role=Role.ADMIN)
        analista = Usuario(id=str(uuid.uuid4()), email="analista@contabil.com", hashed_password=get_password_hash("analista123"), nome="Analista", role=Role.ANALISTA)
        auditor = Usuario(id=str(uuid.uuid4()), email="auditor@contabil.com", hashed_password=get_password_hash("auditor123"), nome="Auditor", role=Role.AUDITOR)
        uow.session.add_all([admin, analista, auditor])
        uow.commit()
    return {"message": "Usuários criados"}
