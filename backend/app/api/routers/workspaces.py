from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, UUID4

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Empresa, Usuario, ClientSchemaMapping

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

class EmpresaResponse(BaseModel):
    id: UUID4
    cnpj: str
    razao_social: str
    nome_fantasia: str
    
    class Config:
        from_attributes = True

class MappingResponse(BaseModel):
    id: str
    file_signature: str
    mapping_json: Dict[str, str]
    
    class Config:
        from_attributes = True

@router.get("/empresas", response_model=List[EmpresaResponse])
def listar_empresas_do_usuario(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna a lista de empresas (workspaces) a que o usuário tem acesso.
    Para ADMINs, pode retornar todas. Para Analistas, retorna a empresa vinculada.
    """
    if current_user.role == "ADMIN" and not current_user.empresa_id:
        empresas = db.query(Empresa).all()
    else:
        # Se for um usuário vinculado a uma empresa
        empresas = db.query(Empresa).filter(Empresa.id == current_user.empresa_id).all()
        
    return empresas

@router.get("/{empresa_id}/mappings", response_model=List[MappingResponse])
def listar_mapeamentos(
    empresa_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista a 'memória' de mapeamentos de planilhas de uma empresa específica.
    """
    if current_user.role != "ADMIN" and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado a este workspace.")
        
    mappings = db.query(ClientSchemaMapping).filter(ClientSchemaMapping.empresa_id == empresa_id).all()
    return mappings

@router.post("/{empresa_id}/mappings/{signature}")
def atualizar_mapeamento(
    empresa_id: UUID4,
    signature: str,
    mapping_payload: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Permite que o Front-End salve um mapeamento manual feito pelo usuário para uma assinatura específica.
    """
    if current_user.role != "ADMIN" and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado a este workspace.")
        
    mapping = db.query(ClientSchemaMapping).filter_by(
        empresa_id=empresa_id,
        file_signature=signature
    ).first()
    
    if mapping:
        mapping.mapping_json = mapping_payload
    else:
        mapping = ClientSchemaMapping(
            empresa_id=empresa_id,
            file_signature=signature,
            mapping_json=mapping_payload
        )
        db.add(mapping)
        
    db.commit()
    return {"status": "Mapeamento salvo na memória do tenant."}
