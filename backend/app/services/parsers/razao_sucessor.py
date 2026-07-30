import logging
import pandas as pd
from sqlalchemy.orm import Session
from app.models.domain import TipoArquivo, LancamentoContabil, TipoMovimentacao
from app.services.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class RazaoSucessorAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.RAZAO:
            return False
        # Apenas tenta ler o header usando calamine, que ignora XML corrompido
        try:
            df = pd.read_excel(file_path, nrows=5, engine="calamine")
            # Valida as colunas ou layout do Razão
            # Se for um Razão genérico
            return True
        except Exception as e:
            logger.debug(f"RazaoSucessorAdapter falhou em can_parse: {e}")
        return False

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando RazaoSucessorAdapter para arquivo {file_path}")
        try:
            df = pd.read_excel(file_path, engine="calamine")
        except Exception as e:
            logger.error(f"Erro ao ler Razão com calamine: {e}")
            raise e
            
        df = pd.read_excel(file_path, engine="calamine", header=None)
        
        novos_lancamentos = 0
        current_date = None
        
        import re
        
        for idx, row in df.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            # Check if it's a date row (e.g. 01/06/2026)
            if re.match(r'^\d{2}/\d{2}/\d{4}$', col0):
                parsed = self._parse_date(col0)
                if parsed:
                    current_date = parsed
                continue
                
            if not current_date:
                continue
                
            if not col0 or col0 == "Histórico" or "Saldo" in col0 or col0.startswith("EMPRESA"):
                continue
                
            # It's a transaction row
            historico = col0
            chave_origem = str(row[5]).strip() if pd.notna(row[5]) else ""
            contra = str(row[8]).strip() if pd.notna(row[8]) else ""
            
            # Débito is around col 10
            debito_str = str(row[10]).strip() if pd.notna(row[10]) else ""
            val_debito = self._parse_float(debito_str)
            
            # Crédito is around col 13
            cred_str = str(row[13]).strip() if pd.notna(row[13]) else ""
            val_cred = self._parse_float(cred_str)
            
            valor = 0.0
            tipo = None
            if val_debito > 0:
                valor = val_debito
                tipo = TipoMovimentacao.D
            elif val_cred > 0:
                valor = val_cred
                tipo = TipoMovimentacao.C
                
            if valor == 0.0:
                continue
            
            lanc = LancamentoContabil(
                execucao_id=execucao_id,
                data=current_date,
                historico=historico,
                valor=valor,
                tipo=tipo,
                chave_origem_sci=chave_origem,
                conta_contrapartida=contra
            )
            db_session.add(lanc)
            novos_lancamentos += 1
            
        db_session.commit()
        logger.info(f"RazaoSucessorAdapter: {novos_lancamentos} lançamentos inseridos")
        return True
