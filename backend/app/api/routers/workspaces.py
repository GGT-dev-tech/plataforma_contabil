from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Empresa, Usuario, ClientSchemaMapping, Role

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

class EmpresaResponse(BaseModel):
    id: str
    cnpj: str
    razao_social: str
    nome_fantasia: str
    import_config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class EmpresaCreate(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: str

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
    if current_user.role == Role.ADMIN and not current_user.empresa_id:
        empresas = db.query(Empresa).all()
    else:
        empresas = db.query(Empresa).filter(Empresa.id == current_user.empresa_id).all()
    
    # Serialize UUIDs to string for JSON response
    return [
        EmpresaResponse(
            id=str(e.id),
            cnpj=e.cnpj or '',
            razao_social=e.razao_social or '',
            nome_fantasia=e.nome_fantasia or '',
            import_config=e.import_config
        ) for e in empresas
    ]

@router.post("/empresas", response_model=EmpresaResponse, status_code=201)
def criar_empresa(
    payload: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cadastra uma nova Empresa (Workspace). 
    Somente ADMINS podem cadastrar novas empresas livremente.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Apenas administradores podem cadastrar novos clientes.")
        
    # Verificar se já existe CNPJ
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == payload.cnpj).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="Empresa com este CNPJ já cadastrada.")
        
    import uuid
    nova_empresa = Empresa(
        id=str(uuid.uuid4()),
        cnpj=payload.cnpj,
        razao_social=payload.razao_social,
        nome_fantasia=payload.nome_fantasia
    )
    
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    
    return nova_empresa

@router.put("/empresas/{empresa_id}/import-config")
def atualizar_import_config(
    empresa_id: UUID4,
    import_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza as configurações de importação (De-Para) do Workspace.
    """
    if current_user.role != "ADMIN" and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado a este workspace.")
        
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Workspace não encontrado.")
        
    empresa.import_config = import_config
    db.commit()
    
    return {"status": "Configurações de importação atualizadas."}

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
