import pandas as pd
import re
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.parsers.base import ParserBase
from app.parsers.models import ParserResult
from app.services.normalization import NormalizationService
from app.models.domain import (
    Despesa, ParcelaDespesa, Fornecedor, Projeto, 
    CategoriaFinanceira, ImportacaoArquivo
)
from app.parsers.patterns.common import CommonPatterns

class StagingDespesa:
    def __init__(self, raw_dict: dict):
        self.raw = raw_dict
        
    @property
    def id_despesa_origem(self): return self.raw.get('ID')
    
    @property
    def id_parcela_origem(self): return self.raw.get('ID Parcela')
    
    @property
    def fornecedor_original(self): return self.raw.get('Fornecedor')
    
    @property
    def fornecedor_normalizado(self):
        return NormalizationService.normalize_fornecedor(self.fornecedor_original)
        
    @property
    def data_emissao(self): 
        val = self.raw.get('Data de competência')
        if pd.isna(val): return None
        if isinstance(val, str):
            # Validação via regex padrão (opcional, pois pandas tbm trata)
            if CommonPatterns.DATE_PTBR.search(val):
                return pd.to_datetime(val, format='%d/%m/%Y', errors='coerce').date()
        return val.date() if hasattr(val, 'date') else None
    
    @property
    def data_vencimento(self): 
        val = self.raw.get('Vencimento parcela')
        if pd.isna(val): return None
        if isinstance(val, str):
            return pd.to_datetime(val, format='%d/%m/%Y', errors='coerce').date()
        return val.date() if hasattr(val, 'date') else None

    @property
    def valor_total(self): 
        v = self.raw.get('Valor total')
        return Decimal(str(v)) if pd.notna(v) else Decimal('0.0')

    @property
    def valor_parcela(self): 
        v = self.raw.get('Valor parcela')
        return Decimal(str(v)) if pd.notna(v) else Decimal('0.0')


class ExcelDespesasParser(ParserBase):
    @property
    def name(self) -> str:
        return "Excel Despesas Parser"
        
    @property
    def version(self) -> str:
        return "1.1"

    @property
    def supported_types(self) -> List[str]:
        return [".xlsx", ".xls"]

    def extract(self, file_path: str, result: ParserResult) -> List[StagingDespesa]:
        df = pd.read_excel(file_path)
        result.metrics.linhas_lidas = len(df)
        
        if 'Tipo' in df.columns:
            df = df[df['Tipo'] == 'Despesa']
            
        records = df.to_dict(orient='records')
        staging = []
        for r in records:
            if pd.notna(r.get('ID')):
                staging.append(StagingDespesa(r))
            else:
                result.metrics.linhas_descartadas += 1
                
        result.metrics.linhas_validas = len(staging)
        return staging

    def validate(self, staging_data: List[StagingDespesa], result: ParserResult) -> bool:
        is_valid = True
        for item in staging_data:
            if not item.id_despesa_origem or not item.id_parcela_origem:
                result.errors.append("Falta de UUID de origem em despesa ou parcela.")
                result.metrics.erros += 1
                is_valid = False
        return is_valid
        
    def transform(self, staging_data: List[StagingDespesa], result: ParserResult) -> Dict[str, Any]:
        canonical = {
            "fornecedores": {},
            "projetos": {},
            "categorias": {},
            "despesas": {},
            "parcelas": {}
        }
        
        for stg in staging_data:
            fn_norm = stg.fornecedor_normalizado
            if fn_norm not in canonical["fornecedores"]:
                canonical["fornecedores"][fn_norm] = Fornecedor(
                    nome=stg.fornecedor_original,
                    nome_normalizado=fn_norm
                )
                
            proj_name = stg.raw.get('Projeto')
            if pd.notna(proj_name):
                if proj_name not in canonical["projetos"]:
                    canonical["projetos"][proj_name] = Projeto(nome=str(proj_name))
            
            cat_name = stg.raw.get('Categoria financeira')
            if pd.notna(cat_name):
                if cat_name not in canonical["categorias"]:
                    canonical["categorias"][cat_name] = CategoriaFinanceira(nome=str(cat_name))

            d_id = str(stg.id_despesa_origem)
            if d_id not in canonical["despesas"]:
                val = abs(stg.valor_total)
                canonical["despesas"][d_id] = Despesa(
                    id_uuid_origem=d_id,
                    valor_total=val,
                    data_emissao=stg.data_emissao
                )
                canonical["despesas"][d_id]._temp_fornecedor = fn_norm
                canonical["despesas"][d_id]._temp_projeto = proj_name if pd.notna(proj_name) else None
                canonical["despesas"][d_id]._temp_cat = cat_name if pd.notna(cat_name) else None
            
            p_id = str(stg.id_parcela_origem)
            if p_id not in canonical["parcelas"]:
                val_parc = abs(stg.valor_parcela)
                canonical["parcelas"][p_id] = ParcelaDespesa(
                    id_parcela_origem=p_id,
                    valor=val_parc,
                    data_vencimento=stg.data_vencimento
                )
                canonical["parcelas"][p_id]._temp_despesa = d_id
                
        return canonical

    def load(self, canonical_data: Dict[str, Any], importacao: ImportacaoArquivo, db_session: Session) -> None:
        for f in canonical_data["fornecedores"].values(): 
            f.arquivo_origem = importacao.id
            f.origem_sistema = "EXCEL_DESPESA"
            db_session.add(f)
            
        for p in canonical_data["projetos"].values(): 
            p.arquivo_origem = importacao.id
            p.origem_sistema = "EXCEL_DESPESA"
            db_session.add(p)
            
        for c in canonical_data["categorias"].values(): 
            c.arquivo_origem = importacao.id
            c.origem_sistema = "EXCEL_DESPESA"
            db_session.add(c)
            
        for d in canonical_data["despesas"].values():
            d.arquivo_origem = importacao.id
            d.origem_sistema = "EXCEL_DESPESA"
            d.fornecedor = canonical_data["fornecedores"][d._temp_fornecedor]
            if d._temp_projeto: d.projeto = canonical_data["projetos"][d._temp_projeto]
            if d._temp_cat: d.categoria = canonical_data["categorias"][d._temp_cat]
            db_session.add(d)
            
        for p in canonical_data["parcelas"].values():
            p.arquivo_origem = importacao.id
            p.origem_sistema = "EXCEL_DESPESA"
            p.despesa = canonical_data["despesas"][p._temp_despesa]
            db_session.add(p)
