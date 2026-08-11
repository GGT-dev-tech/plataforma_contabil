import logging
import uuid
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, StagingRegistro, TipoStaging, ExecucaoPipeline
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class RazaoSucessorAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.RAZAO:
            return False
            
        file_lower = file_path.lower()
        if file_lower.endswith('.pdf'):
            try:
                with pdfplumber.open(file_path) as pdf:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    if "Razão nº" in first_page_text or "contábil SCI" in first_page_text or "Lote" in first_page_text:
                        return True
            except Exception as e:
                logger.debug(f"RazaoSucessorAdapter PDF can_parse error: {e}")
            return False

        if not file_lower.endswith(('.xlsx', '.csv', '.xls')):
            return False
            
        try:
            df = pd.read_excel(file_path, nrows=5, engine="calamine", header=None)
            text_content = " ".join([str(val) for val in df.values.flatten() if pd.notna(val)])
            if "Razão" in text_content or "Histórico" in text_content or "Débito" in text_content:
                return True
        except Exception as e:
            logger.debug(f"RazaoSucessorAdapter falhou em can_parse: {e}")
        return False

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando RazaoSucessorAdapter para arquivo {file_path}")
        
        execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
        empresa_id = execucao.empresa_id if execucao else None

        if file_path.lower().endswith('.pdf'):
            return self._parse_pdf(file_path, db_session, execucao_id, empresa_id)
        else:
            return self._parse_excel(file_path, db_session, execucao_id, empresa_id)

    def _parse_pdf(self, file_path: str, db_session: Session, execucao_id: str, empresa_id: str) -> bool:
        novos_lancamentos = 0
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

                    # Check if date line (Ex: 01/06/2026)
                    if re.match(r'^\d{2}/\d{2}/\d{4}$', line_clean):
                        try:
                            current_date = datetime.strptime(line_clean, "%d/%m/%Y").date()
                        except Exception:
                            pass
                        continue

                    if not current_date:
                        continue

                    if "Histórico" in line_clean or "EMPRESA:" in line_clean or "Saldo anterior" in line_clean or "contábil SCI" in line_clean or "Saldo atual" in line_clean:
                        continue

                    # Match SCI Razão transaction line
                    # Ex: Vlr. Ref. Pix enviado: "Cp :91159764-Pema Beneficiamento" LANCA 40088 1909 2.200,20
                    # Ex: Pix enviado: "Cp :60701190-AUTO POSTO VILA ROMANA LTDA" 40070 370,05
                    match = re.search(r'^(.*?)\s+(?:LANCA\s+)?(?:(\d{4,6})\s+)?(?:(\d{1,5})\s+)?([\d\.]+\,\d{2})$', line_clean)
                    if match:
                        historico = match.group(1).strip()
                        lote = match.group(2) or ""
                        contra = match.group(3) or ""
                        val_str = match.group(4).strip()

                        valor = self._parse_float(val_str)
                        if valor == 0.0:
                            continue

                        # Check if line indicates credit (recebido / resgate) or debit
                        is_recebimento = "recebido" in historico.lower() or "resgate" in historico.lower()
                        
                        stag = StagingRegistro(
                            id=str(uuid.uuid4()),
                            execucao_id=execucao_id,
                            empresa_id=empresa_id,
                            tipo=TipoStaging.EXTRATO,
                            data=current_date,
                            descricao=historico[:255],
                            valor=valor if is_recebimento else -valor,
                            conta_origem=lote,
                            conta_destino=contra,
                            processado=False
                        )
                        db_session.add(stag)
                        novos_lancamentos += 1

        db_session.commit()
        logger.info(f"RazaoSucessorAdapter (PDF): {novos_lancamentos} lançamentos inseridos")
        return True

    def _parse_excel(self, file_path: str, db_session: Session, execucao_id: str, empresa_id: str) -> bool:
        try:
            df = pd.read_excel(file_path, engine="calamine", header=None)
        except Exception as e:
            logger.error(f"Erro ao ler Razão com calamine: {e}")
            raise e
            
        novos_lancamentos = 0
        current_date = None
        
        for idx, row in df.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            if re.match(r'^\d{2}/\d{2}/\d{4}$', col0):
                parsed = self._parse_date(col0)
                if parsed:
                    current_date = parsed
                continue
                
            if not current_date:
                continue
                
            if not col0 or col0 == "Histórico" or "Saldo" in col0 or "EMPRESA" in col0 or col0.startswith("Razão") or col0.startswith("nan"):
                continue
                
            historico = col0
            chave_origem = str(row[5]).strip() if len(row) > 5 and pd.notna(row[5]) else ""
            contra = str(row[8]).strip() if len(row) > 8 and pd.notna(row[8]) else ""
            
            debito_str = str(row[10]).strip() if len(row) > 10 and pd.notna(row[10]) else ""
            val_debito = self._parse_float(debito_str)
            
            cred_str = str(row[13]).strip() if len(row) > 13 and pd.notna(row[13]) else ""
            val_cred = self._parse_float(cred_str)
            
            valor = 0.0
            if val_debito > 0:
                valor = val_debito
            elif val_cred > 0:
                valor = val_cred
                
            if valor == 0.0:
                continue
            
            stag = StagingRegistro(
                id=str(uuid.uuid4()),
                execucao_id=execucao_id,
                empresa_id=empresa_id,
                tipo=TipoStaging.EXTRATO,
                data=current_date,
                descricao=historico[:255],
                valor=valor,
                conta_origem=chave_origem,
                conta_destino=contra,
                processado=False
            )
            db_session.add(stag)
            novos_lancamentos += 1
            
        db_session.commit()
        logger.info(f"RazaoSucessorAdapter (Excel): {novos_lancamentos} lançamentos inseridos")
        return True
