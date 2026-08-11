import logging
import pandas as pd
from sqlalchemy.orm import Session
import uuid
from app.models.domain import (
    TipoArquivo, TipoStaging, StagingRegistro, ExecucaoPipeline
)
from app.contexts.staging_ingestion.parsers.base import ImportAdapter
from app.services.heuristic_mapper import HeuristicMapper

logger = logging.getLogger(__name__)

class GenericSpreadsheetAdapter(ImportAdapter):
    """
    Parser universal de planilhas. 
    Usa o Motor Heurístico para identificar as colunas canônicas
    em formatos caóticos de clientes.
    """
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        # Pega tudo que for planilha e não foi capturado pelos ERPs específicos
        return file_path.lower().endswith(('.xlsx', '.csv', '.xls'))
        
    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando GenericSpreadsheetAdapter (Motor Heurístico) para {file_path}")
        
        # Lê o arquivo
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        headers = df.columns.tolist()
        
        # Recupera Empresa vinculada à execução para checar a memória do Mapeamento
        execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
        empresa_id = str(execucao.empresa_id) if execucao and execucao.empresa_id else None
        
        # 1. Pede para a Inteligência Local o De-Para
        mapping = HeuristicMapper.get_or_infer_mapping(db_session, empresa_id, headers)
        
        # O mapping é um dicionário: {"Nome Estranho da Coluna": "valor"}
        # Vamos inverter para facilitar a busca do df: {"valor": "Nome Estranho da Coluna"}
        canonical_to_raw = {v: k for k, v in mapping.items()}
        
        logger.info(f"Mapeamento Heurístico concluído: {mapping}")
        
        # Identifica o tipo de staging com base no tipo esperado na execução (Despesa vs Extrato)
        # Assumiremos Despesa se não especificado, mas ideal seria buscar da execucao.tipo_arquivo
        tipo_staging = TipoStaging.DESPESA
        if execucao and execucao.tipo_arquivo == TipoArquivo.EXTRATO:
            tipo_staging = TipoStaging.MOVIMENTACAO_BANCARIA
        
        registros_inseridos = 0
        
        for idx, row in df.iterrows():
            # Extração segura das colunas canônicas
            data_raw = row.get(canonical_to_raw.get('data', '')) if 'data' in canonical_to_raw else None
            valor_raw = row.get(canonical_to_raw.get('valor', '')) if 'valor' in canonical_to_raw else None
            descricao_raw = row.get(canonical_to_raw.get('descricao', '')) if 'descricao' in canonical_to_raw else ""
            fornecedor_raw = row.get(canonical_to_raw.get('fornecedor', '')) if 'fornecedor' in canonical_to_raw else ""
            categoria_raw = row.get(canonical_to_raw.get('categoria', '')) if 'categoria' in canonical_to_raw else ""
            
            # Formatação Básica (pula linhas vazias)
            if pd.isna(valor_raw) or not valor_raw: continue
            
            valor_float = self._parse_float(valor_raw)
            if valor_float == 0.0: continue
            
            data_parsed = self._parse_date(data_raw)
            
            stag = StagingRegistro(
                id=str(uuid.uuid4()),
                execucao_id=execucao_id,
                tipo=tipo_staging,
                data=data_parsed,
                valor=valor_float,
                descricao=str(descricao_raw),
                entidade_nome=str(fornecedor_raw),
                categoria=str(categoria_raw) if categoria_raw else None,
                processado=False,
                empresa_id=execucao.empresa_id if execucao else None
            )
            db_session.add(stag)
            registros_inseridos += 1
            
        db_session.commit()
        
        # Salva a memória para as próximas vezes (após processamento bem-sucedido)
        if empresa_id:
            HeuristicMapper.save_mapping(db_session, empresa_id, headers, mapping)
            
        logger.info(f"GenericSpreadsheetAdapter: {registros_inseridos} registros inseridos via Heurística.")
        return True
