import uuid
from typing import List
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.obra import Obra
from app.contexts.conectores_erp.service import ConectorErpService

class SyncObrasCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, erp_name: str) -> List[Obra]:
        if not uow.tenant_id:
            raise ValueError("Sincronização exige um tenant_id válido.")
            
        service = ConectorErpService()
        obras_brutas = service.fetch_obras(erp_name)
        
        novas_obras = []
        for obra_data in obras_brutas:
            # O get_by_field no repositório já garante o filtro do tenant_id
            existente = uow.obras.get_by_field(uow.session, "codigo_interno", str(obra_data["id"]))
            
            if not existente:
                nova = Obra(
                    id=str(uuid.uuid4()),
                    empresa_id=uow.tenant_id,
                    nome=obra_data["name"],
                    codigo_interno=str(obra_data["id"]),
                    codigo_cno=obra_data.get("cno"),
                    endereco_obra=obra_data.get("address"),
                    uf=obra_data.get("state"),
                    tipo="CONSTRUCAO",
                    status="ATIVO",
                    regime_tributario="RET" if "Residencial" in obra_data["name"] else "NORMAL",
                    patrimonio_afetacao=True if "Residencial" in obra_data["name"] else False,
                    percentual_avanco_fisico=0.0
                )
                uow.session.add(nova)
                novas_obras.append(nova)
                
        if novas_obras:
            uow.commit()
            
        return novas_obras
