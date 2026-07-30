import logging
import pandas as pd
import re
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, ExtratoBancario, MovimentacaoBancaria, TipoMovimentacao
from app.services.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class ExtratoInterAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.EXTRATO:
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
        # Example: "1 de Junho de 2026"
        from datetime import date
        months = {
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
            "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
            "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }
        match = re.search(r'(\d+)\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month_str = match.group(2).capitalize()
            year = int(match.group(3))
            month = months.get(month_str)
            if month:
                return date(year, month, day)
        return None

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando ExtratoInterAdapter para arquivo {file_path}")
        df = pd.read_excel(file_path, header=None)
        
        extrato = ExtratoBancario()
        db_session.add(extrato)
        db_session.flush()
        
        current_date = None
        novos_movimentos = 0
        
        for idx, row in df.iterrows():
            col0 = str(row[0]) if pd.notna(row[0]) else ""
            col1 = str(row[1]) if len(row) > 1 and pd.notna(row[1]) else ""
            
            # Checar se é linha de cabeçalho de data
            # Ex: "1 de Junho de 2026 Saldo do dia: R$ 34.255,05"
            parsed_date = self._parse_portuguese_date(col0)
            if parsed_date:
                current_date = parsed_date
                continue
                
            if not current_date:
                continue # Ainda estamos no cabeçalho geral
                
            # Se for transação, a coluna 0 tem o histórico (ex: Pix enviado) e a coluna 1 tem o valor (ex: -R$ 239,00)
            if "Pix" in col0 or "TED" in col0 or "Pagamento" in col0 or col0.startswith("Tarifa"):
                valor = self._parse_float(col1)
                if valor == 0.0:
                    continue
                    
                tipo = TipoMovimentacao.D if valor < 0 else TipoMovimentacao.C
                
                mov = MovimentacaoBancaria(
                    execucao_id=execucao_id,
                    extrato_id=extrato.id,
                    data=current_date,
                    historico=col0.strip(),
                    descricao_original=col0.strip(),
                    valor=valor,
                    tipo=tipo,
                    linha_origem=idx + 1
                )
                db_session.add(mov)
                novos_movimentos += 1
                
        db_session.commit()
        logger.info(f"ExtratoInterAdapter: {novos_movimentos} movimentos inseridos")
        return True
