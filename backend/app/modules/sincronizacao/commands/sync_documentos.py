import uuid
from typing import List
from datetime import datetime
from app.core.uow import SQLAlchemyUnitOfWork
from app.models.documento_fiscal import DocumentoFiscalV2, TipoDocumentoFiscal, NaturezaOperacao
from app.contexts.conectores_erp.service import ConectorErpService

class SyncDocumentosCommandHandler:
    @staticmethod
    def execute(uow: SQLAlchemyUnitOfWork, obra_id: str, erp_name: str) -> List[DocumentoFiscalV2]:
        if not uow.tenant_id:
            raise ValueError("Sincronização exige um tenant_id válido.")
            
        obra = uow.obras.get(uow.session, obra_id)
        if not obra:
            raise ValueError("Obra não encontrada ou não pertence a este tenant.")
            
        service = ConectorErpService()
        docs_brutos = service.fetch_documentos(obra.codigo_interno, erp_name=erp_name)
        
        novos_docs = []
        for doc in docs_brutos:
            numero = doc["invoiceNumber"]
            # Verifica se já existe - o BaseRepository não tem um get_by_fields (plural) por padrão, 
            # mas podemos usar a session com o filtro do tenant
            existente = uow.session.query(DocumentoFiscalV2).filter(
                DocumentoFiscalV2.empresa_id == uow.tenant_id,
                DocumentoFiscalV2.obra_id == obra.id,
                DocumentoFiscalV2.numero == numero
            ).first()
            
            if not existente:
                tipo = TipoDocumentoFiscal.NFE if "NFE" in doc["type"] else TipoDocumentoFiscal.NFSE
                natureza = NaturezaOperacao.MATERIAL if "MATERIAL" in doc["type"] else NaturezaOperacao.SERVICO
                
                novo = DocumentoFiscalV2(
                    id=str(uuid.uuid4()),
                    empresa_id=uow.tenant_id,
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
                uow.session.add(novo)
                novos_docs.append(novo)
                
        if novos_docs:
            uow.commit()
            
        return novos_docs
