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
            logger.info(f"Extraindo dados via GenericPDFAdapter de {file_path}")
            
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
            
            current_date = date.today()
            registros_inseridos = 0

            for text_line in extracted_lines:
                if len(text_line) < 5:
                    continue
                
                # Try to extract date
                date_match = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', text_line)
                if date_match:
                    try:
                        current_date = datetime.strptime(date_match.group(1), "%d/%m/%Y").date()
                    except Exception:
                        pass
                        
                # Match monetary values (e.g., -R$ 1.234,56, R$ 500,00, -1.234,56, 370,05)
                val_match = re.search(r'(-?(?:R\$\s*)?[\d\.]+\,\d{2})', text_line)
                if not val_match:
                    continue
                    
                val_str = val_match.group(1)
                valor = self._parse_float(val_str)
                if valor == 0.0:
                    continue
                
                filename_lower = file_path.lower()
                tipo_st = TipoStaging.EXTRATO
                if 'razao' in filename_lower or 'despesa' in filename_lower:
                    tipo_st = TipoStaging.DESPESA
                elif 'extrato' in filename_lower:
                    tipo_st = TipoStaging.EXTRATO
                
                reg = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=tipo_st, 
                    data=current_date,
                    descricao=text_line[:255],
                    valor=valor,
                    processado=False
                )
                db_session.add(reg)
                registros_inseridos += 1
                
            db_session.commit()
            logger.info(f"GenericPDFAdapter: {registros_inseridos} registros inseridos para {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Falha ao ler PDF {file_path}: {e}")
            return False
