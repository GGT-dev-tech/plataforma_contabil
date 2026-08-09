import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, TipoStaging, StagingRegistro, ExecucaoPipeline
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class GenericXMLAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        return file_path.lower().endswith('.xml')
        
    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        try:
            logger.info(f"Extraindo dados via XMLParser de {file_path}")
            
            execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
            empresa_id = execucao.empresa_id if execucao else None
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Limpa namespaces para facilitar busca
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
                    
            # Tentar encontrar blocos de NotaFiscal ou pagamentos
            # Fallback genérico: varrer elementos chave
            nfe_nodes = root.findall('.//NFe') or root.findall('.//NotaFiscal') or [root]
            
            for node in nfe_nodes:
                data_emissao = node.find('.//dhEmi') or node.find('.//DataEmissao')
                valor_total = node.find('.//vNF') or node.find('.//ValorTotal')
                fornecedor = node.find('.//xNome') or node.find('.//RazaoSocial')
                
                data_val = date.today()
                if data_emissao is not None and data_emissao.text:
                    try:
                        # ex: 2023-10-25T14:30:00-03:00
                        data_str = data_emissao.text[:10]
                        data_val = datetime.strptime(data_str, "%Y-%m-%d").date()
                    except:
                        pass
                        
                valor = 0.0
                if valor_total is not None and valor_total.text:
                    try:
                        valor = float(valor_total.text)
                    except:
                        pass
                        
                descricao = "Nota Fiscal / XML Genérico"
                if fornecedor is not None and fornecedor.text:
                    descricao = f"NF Fornecedor: {fornecedor.text}"
                    
                reg = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=TipoStaging.DESPESA,
                    data=data_val,
                    descricao=descricao[:255],
                    valor=valor,
                    documento=None,
                    status="AGUARDANDO_REVISAO"
                )
                db_session.add(reg)
                
            db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Falha ao ler XML {file_path}: {e}")
            return False
