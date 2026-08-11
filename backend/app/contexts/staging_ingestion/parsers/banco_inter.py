import logging
import pandas as pd
import pdfplumber
import re
import uuid
from datetime import date
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, TipoStaging, StagingRegistro, ExecucaoPipeline
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class ExtratoInterAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.EXTRATO:
            return False
            
        file_lower = file_path.lower()
        if file_lower.endswith('.pdf'):
            try:
                with pdfplumber.open(file_path) as pdf:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    if "Banco Inter" in first_page_text or "Saldo do dia:" in first_page_text or "EMPREENDIMENTOS" in first_page_text:
                        return True
            except Exception as e:
                logger.debug(f"ExtratoInterAdapter PDF can_parse error: {e}")
            return False

        if not file_lower.endswith(('.xlsx', '.csv', '.xls')):
            return False
        
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
        
        execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
        empresa_id = execucao.empresa_id if execucao else None

        if file_path.lower().endswith('.pdf'):
            return self._parse_pdf(file_path, db_session, execucao_id, empresa_id)
        else:
            return self._parse_excel(file_path, db_session, execucao_id, empresa_id)

    def _parse_pdf(self, file_path: str, db_session: Session, execucao_id: str, empresa_id: str) -> bool:
        novos_movimentos = 0
        current_date = None

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line in lines:
                    line_clean = line.strip()
                    if not line_clean:
                        continue

                    # Check for date header line
                    parsed_date = self._parse_portuguese_date(line_clean)
                    if parsed_date:
                        current_date = parsed_date
                        continue

                    if not current_date:
                        continue

                    # Match transaction line with R$ value at the end
                    # Ex: Pix enviado: "Cp :10573521-PIX Marketplace" -R$ 239,00
                    # Ex: Resgate Imediato Fundo: "INTER RESGATE 24H FIC FIRF RL" R$ 149.795,17
                    match = re.search(r'^(.*?)\s+((-?R\$\s*[\d\.,]+)|(-?[\d\.]+\,\d{2}))$', line_clean)
                    if match:
                        descricao = match.group(1).strip()
                        val_str = match.group(2).strip()

                        # Skip header lines
                        if "Saldo do dia" in descricao or "Saldo total" in descricao or "Solicitado em" in descricao:
                            continue

                        valor = self._parse_float(val_str)
                        if valor == 0.0:
                            continue

                        mov = StagingRegistro(
                            id=str(uuid.uuid4()),
                            execucao_id=execucao_id,
                            empresa_id=empresa_id,
                            tipo=TipoStaging.EXTRATO,
                            data=current_date,
                            descricao=descricao[:255],
                            valor=valor,
                            processado=False
                        )
                        db_session.add(mov)
                        novos_movimentos += 1

        db_session.commit()
        logger.info(f"ExtratoInterAdapter (PDF): {novos_movimentos} movimentos inseridos")
        return True

    def _parse_excel(self, file_path: str, db_session: Session, execucao_id: str, empresa_id: str) -> bool:
        df = pd.read_excel(file_path, header=None)
        current_date = None
        novos_movimentos = 0
        
        for idx, row in df.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            col1 = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else ""
            
            if not col0 or "Solicitado em" in col0 or "CPF/CNPJ" in col0 or "Período:" in col0 or col0.startswith("nan"):
                continue
                
            parsed_date = self._parse_portuguese_date(col0)
            if parsed_date:
                current_date = parsed_date
                continue
                
            if not current_date:
                continue
                
            if col1 and any(char.isdigit() for char in col1):
                valor = self._parse_float(col1)
                if valor == 0.0:
                    continue
                    
                mov = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=TipoStaging.EXTRATO,
                    data=current_date,
                    descricao=col0[:255],
                    valor=valor,
                    processado=False
                )
                db_session.add(mov)
                novos_movimentos += 1
                
        db_session.commit()
        logger.info(f"ExtratoInterAdapter (Excel): {novos_movimentos} movimentos inseridos")
        return True
