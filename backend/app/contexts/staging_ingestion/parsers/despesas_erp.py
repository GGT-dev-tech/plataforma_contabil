import logging
import pandas as pd
from sqlalchemy.orm import Session
import uuid
from app.models.domain import (
    TipoArquivo, TipoStaging, StagingRegistro
)
from app.contexts.staging_ingestion.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class DespesasERPAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.DESPESA: return False
        if not file_path.lower().endswith(('.xlsx', '.csv', '.xls')): return False
        
        try:
            # Lemos a primeira linha de dados reais para ver as colunas
            df = pd.read_excel(file_path, nrows=5)
            cols = {str(c).lower().strip() for c in df.columns}
            # Se tiver ID Parcela e Valor parcela, é o ERP Despesas
            if 'id parcela' in cols and 'valor parcela' in cols and 'fornecedor' in cols:
                return True
        except Exception:
            pass
        return False
        
    # Helper methods omitted due to semantic flattening into Staging.
    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando DespesasERPAdapter para arquivo {file_path}")
        df = pd.read_excel(file_path)
        
        # Mapeamento para lower
        df.columns = df.columns.str.lower().str.strip()
        
        novas_parcelas = 0
        
        for idx, row in df.iterrows():
            id_despesa = str(row.get('id', '')).strip()
            if not id_despesa or id_despesa == 'nan' or pd.isna(row.get('id')):
                continue
                
            valor_parcela = self._parse_float(row.get('valor parcela', 0.0))
            if valor_parcela == 0.0:
                continue
                
            parcela_data = self._parse_date(row.get('vencimento parcela'))
            parcela_valor = valor_parcela
            fornecedor_nome = str(row.get('fornecedor', ''))
            
            stag = StagingRegistro(
                id=str(uuid.uuid4()),
                execucao_id=execucao_id,
                tipo=TipoStaging.DESPESA,
                data=parcela_data,
                valor=parcela_valor,
                descricao=f"Nº Doc ERP: {id_despesa}",
                entidade_nome=fornecedor_nome,
                processado=False
            )
            db_session.add(stag)
            novas_parcelas += 1
            
        db_session.commit()
        logger.info(f"DespesasERPAdapter: {novas_parcelas} parcelas inseridas")
        return True
