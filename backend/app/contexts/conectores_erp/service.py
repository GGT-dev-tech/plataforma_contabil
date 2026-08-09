import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models.obra import Obra
from app.models.documento_fiscal import DocumentoFiscalV2, TipoDocumentoFiscal, NaturezaOperacao
from app.contexts.conectores_erp.adapters.sienge import SiengeConnector

class ConectorErpService:
    def __init__(self, db: Session):
        self.db = db
        # Para este MVP, mapeamos apenas o Sienge. Pode ser estendido.
        self.adapters = {
            "sienge": SiengeConnector()
        }
        
    def sincronizar_obras(self, empresa_id: str, erp_name: str = "sienge") -> List[Obra]:
        if erp_name not in self.adapters:
            raise ValueError("ERP não suportado")
            
        adapter = self.adapters[erp_name]
        adapter.autenticar({})
        
        obras_erp = adapter.listar_obras()
        novas_obras = []
        
        for obra_data in obras_erp:
            # Verifica se já existe por código interno / CNO
            existente = self.db.query(Obra).filter(
                Obra.empresa_id == empresa_id,
                Obra.codigo_interno == str(obra_data["id"])
            ).first()
            
            if not existente:
                nova = Obra(
                    id=str(uuid.uuid4()),
                    empresa_id=empresa_id,
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
                self.db.add(nova)
                novas_obras.append(nova)
                
        if novas_obras:
            self.db.commit()
            
        return novas_obras

    def sincronizar_documentos(self, obra_id: str, erp_name: str = "sienge") -> List[DocumentoFiscalV2]:
        obra = self.db.query(Obra).filter(Obra.id == obra_id).first()
        if not obra:
            raise ValueError("Obra não encontrada")
            
        if erp_name not in self.adapters:
            raise ValueError("ERP não suportado")
            
        adapter = self.adapters[erp_name]
        adapter.autenticar({})
        
        # Supondo que 'codigo_interno' é o ID no ERP
        docs_erp = adapter.listar_documentos_fiscais(obra.codigo_interno, "2026-08-01", "2026-08-31")
        novos_docs = []
        
        for doc in docs_erp:
            # Verifica se a nota já foi integrada
            numero = doc["invoiceNumber"]
            existente = self.db.query(DocumentoFiscalV2).filter(
                DocumentoFiscalV2.obra_id == obra.id,
                DocumentoFiscalV2.numero == numero
            ).first()
            
            if not existente:
                tipo = TipoDocumentoFiscal.NFE if "NFE" in doc["type"] else TipoDocumentoFiscal.NFSE
                natureza = NaturezaOperacao.MATERIAL if "MATERIAL" in doc["type"] else NaturezaOperacao.SERVICO
                
                novo = DocumentoFiscalV2(
                    id=str(uuid.uuid4()),
                    empresa_id=obra.empresa_id,
                    obra_id=obra.id,
                    tipo=tipo.name,
                    natureza_operacao=natureza.name,
                    status="VALIDADO",
                    numero=numero,
                    chave_acesso=doc.get("invoiceKey"),
                    data_emissao=datetime.strptime(doc["issueDate"], "%Y-%m-%d"),
                    data_entrada=datetime.utcnow(),
                    emitente_cnpj_cpf=doc["providerCnpj"],
                    emitente_nome=doc["providerName"],
                    valor_bruto=doc["grossValue"],
                    valor_desconto=0,
                    iss_valor=doc["taxes"]["iss"],
                    inss_valor=doc["taxes"]["inss"],
                    ir_valor=doc["taxes"]["irrf"],
                    importado_via=f"API_{erp_name.upper()}"
                )
                self.db.add(novo)
                novos_docs.append(novo)
                
        if novos_docs:
            self.db.commit()
            
        return novos_docs
