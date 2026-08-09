import logging
import pandas as pd
import re
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, TipoStaging, StagingRegistro
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class ExtratoInterAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.EXTRATO: return False
        if not file_path.lower().endswith(('.xlsx', '.csv', '.xls')): return False
        
        try:
            df = pd.read_excel(file_path, nrows=10, header=None)
            text_content = " ".join([str(val) for val in df.values.flatten() if pd.notna(val)])
            if "Banco Inter" in text_content or "CPF/CNPJ:" in text_content:
                return True
        except Exception:
            pass
        return False
        
    def _parse_portuguese_date(self, date_str: str):
        # Example: "1 de Junho de 2026 Saldo do dia: R$ 34.255,05"
        from datetime import date
        months = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
            "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
            "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
        }
        match = re.search(r'(\d+)\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month_str = match.group(2).lower()
            year = int(match.group(3))
            month = months.get(month_str)
            if month:
                return date(year, month, day)
        return None

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando ExtratoInterAdapter para arquivo {file_path}")
        df = pd.read_excel(file_path, header=None)
        
        # Extrato e Despesas serão achatados em StagingRegistro
        
        current_date = None
        novos_movimentos = 0
        
        for idx, row in df.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            col1 = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else ""
            
            # Pula linhas irrelevantes
            if not col0 or "Solicitado em" in col0 or "CPF/CNPJ" in col0 or "Período:" in col0 or col0.startswith("nan"):
                continue
                
            # Checar se é linha de cabeçalho de data
            # Ex: "1 de Junho de 2026 Saldo do dia: R$ 34.255,05"
            parsed_date = self._parse_portuguese_date(col0)
            if parsed_date:
                current_date = parsed_date
                continue
                
            if not current_date:
                continue # Ainda estamos no cabeçalho geral
                
            # Identificar uma transação de verdade
            if col1 and any(char.isdigit() for char in col1):
                # O Inter exporta descrições multilinha às vezes, mas `col1` tem o valor "-R$ 1.974,10"
                valor = self._parse_float(col1)
                if valor == 0.0:
                    continue
                    
                import uuid
                mov = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    tipo=TipoStaging.EXTRATO,
                    data=current_date,
                    descricao=col0,
                    valor=valor,
                    processado=False
                )
                db_session.add(mov)
                novos_movimentos += 1
                
        db_session.commit()
        logger.info(f"ExtratoInterAdapter: {novos_movimentos} movimentos inseridos")
        return True
