import pandas as pd
from io import BytesIO
from typing import BinaryIO
import uuid
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain import (
    Fornecedor, Despesa, ParcelaDespesa,
    ExtratoBancario, MovimentacaoBancaria, TipoMovimentacao,
    LancamentoContabil
)

logger = logging.getLogger(__name__)

def _parse_date(val) -> datetime.date:
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.date()
    try:
        return pd.to_datetime(val, dayfirst=True).date()
    except:
        return None

def _parse_float(val) -> float:
    if pd.isna(val):
        return 0.0
    try:
        if isinstance(val, str):
            val = val.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(val)
    except:
        return 0.0

def parse_despesas(file_stream: BinaryIO, db: Session, execucao_id: str):
    """
    Formato esperado:
    Fornecedor | Valor | Data Vencimento | Documento
    """
    logger.info(f"Iniciando parse_despesas para execucao {execucao_id}")
    try:
        df = pd.read_excel(file_stream) if hasattr(file_stream, 'name') and file_stream.name.endswith((".xlsx", ".xls")) else pd.read_csv(file_stream)
        
        # Mapeamento para MVP (case insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Busca fornecedores existentes para cache
        fornecedores_existentes = {f.nome_normalizado: f for f in db.query(Fornecedor).all()}
        
        novas_parcelas = 0
        for idx, row in df.iterrows():
            # Extrair valores
            fornecedor_nome = str(row.get('fornecedor', f"Fornecedor {idx}")).strip()
            fornecedor_norm = fornecedor_nome.upper()
            
            valor = _parse_float(row.get('valor', 0.0))
            if valor == 0.0:
                continue # Pular linhas vazias
                
            data_vencimento = _parse_date(row.get('data vencimento', row.get('data')))
            documento = str(row.get('documento', '')).strip()
            
            # 1. Obter ou Criar Fornecedor
            forn = fornecedores_existentes.get(fornecedor_norm)
            if not forn:
                forn = Fornecedor(nome=fornecedor_nome, nome_normalizado=fornecedor_norm)
                db.add(forn)
                fornecedores_existentes[fornecedor_norm] = forn
                
            # 2. Criar Despesa
            despesa = Despesa(
                execucao_id=execucao_id,
                fornecedor_id=forn.id,
                valor_total=valor,
                id_uuid_origem=documento
            )
            db.add(despesa)
            db.flush()
            
            # 3. Criar Parcela
            parcela = ParcelaDespesa(
                despesa_id=despesa.id,
                numero_parcela=1,
                valor=valor,
                data_vencimento=data_vencimento,
                id_parcela_origem=documento
            )
            db.add(parcela)
            novas_parcelas += 1
            
        db.commit()
        logger.info(f"parse_despesas concluído: {novas_parcelas} parcelas inseridas")
        return True
    except Exception as e:
        logger.error(f"Erro em parse_despesas: {e}")
        db.rollback()
        raise e

def parse_extrato(file_stream: BinaryIO, db: Session, execucao_id: str):
    """
    Formato esperado:
    Data | Histórico | Valor
    """
    logger.info(f"Iniciando parse_extrato para execucao {execucao_id}")
    try:
        df = pd.read_excel(file_stream) if hasattr(file_stream, 'name') and file_stream.name.endswith((".xlsx", ".xls")) else pd.read_csv(file_stream)
        df.columns = df.columns.str.lower().str.strip()
        
        extrato = ExtratoBancario()
        db.add(extrato)
        db.flush()
        
        novos_movimentos = 0
        for idx, row in df.iterrows():
            data = _parse_date(row.get('data'))
            historico = str(row.get('historico', '')).strip()
            valor = _parse_float(row.get('valor', 0.0))
            
            if pd.isna(row.get('valor')):
                continue
                
            tipo = TipoMovimentacao.D if valor < 0 else TipoMovimentacao.C
            
            mov = MovimentacaoBancaria(
                execucao_id=execucao_id,
                extrato_id=extrato.id,
                data=data,
                historico=historico,
                descricao_original=historico,
                valor=valor,
                tipo=tipo,
                linha_origem=idx + 1
            )
            db.add(mov)
            novos_movimentos += 1
            
        db.commit()
        logger.info(f"parse_extrato concluído: {novos_movimentos} movimentos inseridos")
        return True
    except Exception as e:
        logger.error(f"Erro em parse_extrato: {e}")
        db.rollback()
        raise e

def parse_razao(file_stream: BinaryIO, db: Session, execucao_id: str):
    """
    Formato esperado:
    Data | Conta | Histórico | Valor
    """
    logger.info(f"Iniciando parse_razao para execucao {execucao_id}")
    try:
        df = pd.read_excel(file_stream) if hasattr(file_stream, 'name') and file_stream.name.endswith((".xlsx", ".xls")) else pd.read_csv(file_stream)
        df.columns = df.columns.str.lower().str.strip()
        
        novos_lancamentos = 0
        for idx, row in df.iterrows():
            data = _parse_date(row.get('data'))
            conta = str(row.get('conta', '')).strip()
            historico = str(row.get('historico', '')).strip()
            valor = _parse_float(row.get('valor', 0.0))
            
            if pd.isna(row.get('valor')):
                continue
                
            tipo = TipoMovimentacao.D if valor < 0 else TipoMovimentacao.C
            
            lanc = LancamentoContabil(
                execucao_id=execucao_id,
                data=data,
                historico=historico,
                valor=valor,
                tipo=tipo,
                conta_contrapartida=conta
            )
            db.add(lanc)
            novos_lancamentos += 1
            
        db.commit()
        logger.info(f"parse_razao concluído: {novos_lancamentos} lançamentos inseridos")
        return True
    except Exception as e:
        logger.error(f"Erro em parse_razao: {e}")
        db.rollback()
        raise e
