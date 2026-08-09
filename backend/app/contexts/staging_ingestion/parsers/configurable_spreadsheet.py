import logging
import pandas as pd
from sqlalchemy.orm import Session
import uuid
import datetime
from typing import Dict, Any
from app.models.domain import (
    TipoArquivo, TipoStaging, StagingRegistro
)
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class ConfigurableSpreadsheetParser(ImportAdapter):
    """
    Parser guiado por configurações do Workspace (Cliente).
    """
    
    def __init__(self, import_config: Dict[str, Any], tipo_arquivo: TipoArquivo):
        self.import_config = import_config or {}
        self.tipo_arquivo = tipo_arquivo

    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != self.tipo_arquivo:
            return False
        if not file_path.lower().endswith(('.xlsx', '.csv', '.xls')): 
            return False
        return True
        
    def _parse_float(self, val):
        if pd.isna(val) or val == '' or val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(val)
        except:
            return 0.0

    def _parse_date(self, val):
        if pd.isna(val): return datetime.date.today()
        if isinstance(val, (datetime.datetime, datetime.date)):
            return val.date() if isinstance(val, datetime.datetime) else val
            
        val = str(val).strip()
        try:
            return pd.to_datetime(val, dayfirst=True).date()
        except:
            return datetime.date.today()

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando ConfigurableSpreadsheetParser para {file_path}")
        
        # O mapping é algo como {"col_data": "Data Vencimento", "col_valor": "Valor Parcela", ...}
        mapping = self.import_config.get(self.tipo_arquivo.name, {})
        skip_rows = mapping.get("skip_rows", 0)
        
        col_data = mapping.get("col_data")
        col_valor = mapping.get("col_valor")
        col_descricao = mapping.get("col_descricao")
        col_entidade = mapping.get("col_entidade")
        
        if not col_data or not col_valor:
            logger.error("Configuração de importação incompleta. col_data e col_valor são obrigatórios.")
            return False

        try:
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, skiprows=skip_rows)
            else:
                df = pd.read_excel(file_path, skiprows=skip_rows, engine="calamine")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return False
            
        # Normaliza colunas do DF e da config
        df.columns = df.columns.astype(str).str.strip().str.lower()
        col_data_norm = col_data.strip().lower()
        col_valor_norm = col_valor.strip().lower()
        col_desc_norm = col_descricao.strip().lower() if col_descricao else None
        col_ent_norm = col_entidade.strip().lower() if col_entidade else None

        tipo_staging = getattr(TipoStaging, self.tipo_arquivo.name, TipoStaging.DESPESA)
        
        registros = 0
        for idx, row in df.iterrows():
            # Tentar extrair dados
            try:
                if col_valor_norm not in row:
                    continue
                
                raw_valor = row.get(col_valor_norm)
                valor = self._parse_float(raw_valor)
                if valor == 0.0:
                    continue
                
                raw_data = row.get(col_data_norm)
                data_parsed = self._parse_date(raw_data)
                
                descricao = str(row.get(col_desc_norm, "-")) if col_desc_norm and col_desc_norm in row else "-"
                entidade = str(row.get(col_ent_norm, "")) if col_ent_norm and col_ent_norm in row else None
                
                # Para extrato e dinheiro, normalmente inverter sinal dependendo da coluna não é configurável aqui, mas poderíamos ter "multiplicador_valor: -1"
                multiplicador = mapping.get("multiplicador_valor", 1)
                valor = valor * multiplicador

                stag = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    tipo=tipo_staging,
                    data=data_parsed,
                    valor=valor,
                    descricao=descricao[:255],
                    entidade_nome=entidade[:255] if entidade else None,
                    processado=False
                )
                db_session.add(stag)
                registros += 1
            except Exception as e:
                logger.warning(f"Erro ao parsear linha {idx}: {e}")
                
        db_session.commit()
        logger.info(f"ConfigurableSpreadsheetParser: {registros} registros inseridos no Staging.")
        return True
