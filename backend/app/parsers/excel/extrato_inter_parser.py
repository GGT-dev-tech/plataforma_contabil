import pandas as pd
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.parsers.base import ParserBase
from app.parsers.models import ParserResult
from app.parsers.patterns.inter_patterns import InterPatterns
from app.models.domain import MovimentacaoBancaria, ImportacaoArquivo, TipoMovimentacao

class InterStagingMovimentacao:
    def __init__(self, data: date, historico: str, valor: Decimal, tipo: TipoMovimentacao, codigo_cp: Optional[str] = None):
        self.data = data
        self.historico = historico
        self.valor = valor
        self.tipo = tipo
        self.codigo_cp = codigo_cp

class ExtratoInterParser(ParserBase):
    @property
    def name(self) -> str:
        return "Extrato Inter PDF-Excel Parser"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def supported_types(self) -> List[str]:
        return [".xlsx"]

    def extract(self, file_path: str, result: ParserResult) -> List[InterStagingMovimentacao]:
        # Inter exporta PDF via Excel. Usamos header=None para facilitar o mapeamento de colunas.
        df = pd.read_excel(file_path, header=None, engine='calamine')
        records = df.to_dict(orient='records')
        result.metrics.linhas_lidas = len(records)
        
        staging_records = []
        current_date: Optional[date] = None
        
        for idx, row in enumerate(records):
            col0 = str(row.get(0, '')).strip()
            col1 = str(row.get(1, '')).strip()
            
            if not col0 or col0 == 'nan':
                continue
                
            # Date Propagation Detector
            match_date = InterPatterns.DATA_HEADER.match(col0)
            if match_date:
                dia = int(match_date.group(1))
                mes_str = match_date.group(2).lower()
                ano = int(match_date.group(3))
                mes = InterPatterns.MESES.get(mes_str)
                if mes:
                    current_date = date(ano, mes, dia)
                continue
                
            # Transaction Detector (Possui valor e descrição)
            if current_date and col1 and col1 != 'nan' and 'R$' in col1:
                if 'Saldo do dia' in col0 or col1 == 'Valor':
                    continue # Linha de cabeçalho interno
                    
                # Extrai valor numérico
                is_negative = '-' in col1
                val_str = col1.replace('-R$', '').replace('R$', '').replace('.', '').replace(',', '.').strip()
                try:
                    valor = Decimal(val_str)
                except:
                    continue
                    
                tipo = TipoMovimentacao.D if is_negative else TipoMovimentacao.C
                
                # Handlers Táticos
                codigo_cp = None
                match_cp = InterPatterns.CP_CODE.search(col0)
                if match_cp:
                    codigo_cp = match_cp.group(1)
                    
                staging_records.append(InterStagingMovimentacao(
                    data=current_date,
                    historico=col0,
                    valor=valor,
                    tipo=tipo,
                    codigo_cp=codigo_cp
                ))
            else:
                result.metrics.linhas_descartadas += 1
                
        result.metrics.linhas_validas = len(staging_records)
        return staging_records

    def validate(self, staging_data: List[InterStagingMovimentacao], result: ParserResult) -> bool:
        if not staging_data:
            result.errors.append("Nenhuma movimentação foi extraída do extrato.")
            return False
            
        is_valid = True
        for idx, item in enumerate(staging_data):
            if not item.data:
                result.errors.append(f"Linha {idx} sem data propagada.")
                is_valid = False
            if item.valor <= 0:
                result.errors.append(f"Linha {idx} com valor zerado/inválido.")
                is_valid = False
        return is_valid

    def transform(self, staging_data: List[InterStagingMovimentacao], result: ParserResult) -> List[MovimentacaoBancaria]:
        canonical_records = []
        for stg in staging_data:
            canonical_records.append(MovimentacaoBancaria(
                data=stg.data,
                historico=stg.historico,
                descricao_original=stg.historico,
                valor=stg.valor,
                tipo=stg.tipo,
                codigo_cp=stg.codigo_cp
            ))
        return canonical_records

    def load(self, canonical_data: List[MovimentacaoBancaria], importacao: ImportacaoArquivo, db_session: Session) -> None:
        for mov in canonical_data:
            mov.arquivo_origem = importacao.id
            mov.origem_sistema = "EXTRATO_INTER"
            db_session.add(mov)
