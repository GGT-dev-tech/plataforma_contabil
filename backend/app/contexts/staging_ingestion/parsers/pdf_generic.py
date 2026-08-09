import logging
import uuid
import pdfplumber
import re
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, TipoStaging, StagingRegistro, ExecucaoPipeline
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class GenericPDFAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        return file_path.lower().endswith('.pdf')
        
    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        try:
            logger.info(f"Extraindo dados via PDFPlumber de {file_path}")
            
            # Buscar a empresa_id da execucao
            execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
            empresa_id = execucao.empresa_id if execucao else None
            
            extracted_lines = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            if len(line.strip()) > 5:
                                extracted_lines.append(line.strip())
            
            for i, text_line in enumerate(extracted_lines):
                if len(text_line) < 10: continue
                
                date_match = re.search(r'\d{2}/\d{2}/\d{4}', text_line)
                data_val = date.today()
                if date_match:
                    try:
                        data_val = datetime.strptime(date_match.group(0), "%d/%m/%Y").date()
                    except:
                        pass
                        
                val_match = re.search(r'-?R\$\s*[\d\.,]+', text_line)
                if not val_match:
                    continue
                    
                valor = 0.0
                # Captura tudo, depois extrai o sinal de menos se houver
                match_str = val_match.group(0)
                is_negative = match_str.startswith('-')
                v_str = match_str.replace('-','').replace('R$', '').replace('.', '').replace(',', '.').strip()
                try:
                    valor = float(v_str)
                    if is_negative:
                        valor = -valor
                except:
                    pass
                
                # Inferir o tipo baseado no nome do arquivo
                tipo_st = TipoStaging.EXTRATO
                
                filename_lower = file_path.lower()
                if 'razao' in filename_lower or 'despesa' in filename_lower:
                    tipo_st = TipoStaging.DESPESA
                elif 'extrato' in filename_lower:
                    tipo_st = TipoStaging.EXTRATO
                
                reg = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=tipo_st, 
                    data=data_val,
                    descricao=text_line[:255],
                    valor=valor,
                    processado=False
                )
                db_session.add(reg)
                
            db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Falha ao ler PDF {file_path}: {e}")
            return False
