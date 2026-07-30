import pandas as pd
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.parsers.base import ParserBase
from app.parsers.models import ParserResult
from app.parsers.patterns.sci_patterns import SciPatterns
from app.parsers.patterns.common import CommonPatterns
from app.models.domain import LancamentoContabil, ContaContabil, ImportacaoArquivo

class SciStagingLancamento:
    def __init__(self, data: date, historico: str, valor: Decimal, tipo: str, lote: str, chave: str, conta_contrapartida: str, conta_id: str):
        self.data = data
        self.historico = historico
        self.valor = valor
        self.tipo = tipo
        self.lote = lote
        self.chave_origem_sci = chave
        self.conta_contrapartida = conta_contrapartida
        self.conta_id = conta_id

class SciContextManager:
    """Mantém o contexto de navegação pelo arquivo SCI"""
    def __init__(self):
        self.current_account_code: Optional[str] = None
        self.current_account_desc: Optional[str] = None
        self.current_date: Optional[date] = None

class SciRazaoParser(ParserBase):
    @property
    def name(self) -> str:
        return "Razão Contábil SCI Parser"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def supported_types(self) -> List[str]:
        return [".xlsx", ".xls"]

    def extract(self, file_path: str, result: ParserResult) -> List[SciStagingLancamento]:
        # Componente 1: Reader (usando calamine para evitar quebra de stylesheet)
        df = pd.read_excel(file_path, header=None, engine='calamine')
        records = df.to_dict(orient='records')
        result.metrics.linhas_lidas = len(records)
        
        staging_records = []
        context = SciContextManager()
        
        for idx, row in enumerate(records):
            # A coluna 0 geralmente guarda as quebras ou o Histórico.
            col0 = str(row.get(0, '')).strip()
            if not col0 or col0 == 'nan':
                continue
                
            if col0 in SciPatterns.IGNORAR_HEADERS:
                continue

            # Componente 2: Section Detector (Nova conta contábil)
            match_conta = SciPatterns.CONTA_HEADER.match(col0)
            if match_conta:
                context.current_account_code = match_conta.group(3)
                context.current_account_desc = match_conta.group(4)
                # Reseta data para a nova seção
                context.current_date = None
                continue
                
            # Componente 3: Date Propagation
            match_data = SciPatterns.DATA_ISOLADA.match(col0)
            if match_data:
                dt_str = match_data.group(1)
                context.current_date = pd.to_datetime(dt_str, format='%d/%m/%Y').date()
                continue
                
            # Componente 4: Movement Extractor (Se não for conta nem data solta, e tem lote/chave, é transação)
            # A estrutura identificada:
            # col 0: Histórico
            # col 3: Lote
            # col 5: Chave
            # col 8: Contrapartida
            # col 10 ou 13: Débito ou Crédito
            
            historico = col0
            lote = str(row.get(3, '')).strip()
            chave = str(row.get(5, '')).strip()
            contra = str(row.get(8, '')).strip()
            
            # Se não tem chave ou não é transação padrão, pula (pode ser saldo anterior)
            if not chave or chave == 'nan':
                continue
                
            # Avalia Débito (10 ou 11 ou 12) e Crédito (13 ou 14 ou 15)
            # Como vimos no log, os valores flutuam de coluna devido a mesclagem. 
            # Procuramos por padrão monetário nas colunas de 10 a 16.
            debito_val = None
            credito_val = None
            
            for c in range(10, 13):
                val_str = str(row.get(c, '')).strip()
                if val_str and val_str != 'nan' and CommonPatterns.MONETARY.search(val_str):
                    debito_val = val_str
                    break
                    
            for c in range(13, 17):
                val_str = str(row.get(c, '')).strip()
                if val_str and val_str != 'nan' and CommonPatterns.MONETARY.search(val_str):
                    credito_val = val_str
                    break

            if debito_val:
                clean_val = debito_val.replace('.', '').replace(',', '.')
                staging_records.append(SciStagingLancamento(
                    data=context.current_date,
                    historico=historico,
                    valor=Decimal(clean_val),
                    tipo='D',
                    lote=lote,
                    chave=chave,
                    conta_contrapartida=contra,
                    conta_id=context.current_account_code
                ))
            elif credito_val:
                clean_val = credito_val.replace('.', '').replace(',', '.')
                staging_records.append(SciStagingLancamento(
                    data=context.current_date,
                    historico=historico,
                    valor=Decimal(clean_val),
                    tipo='C',
                    lote=lote,
                    chave=chave,
                    conta_contrapartida=contra,
                    conta_id=context.current_account_code
                ))
            else:
                result.metrics.linhas_descartadas += 1

        result.metrics.linhas_validas = len(staging_records)
        return staging_records

    def validate(self, staging_data: List[SciStagingLancamento], result: ParserResult) -> bool:
        if not staging_data:
            result.errors.append("Nenhum lançamento foi extraído da Razão SCI.")
            return False
            
        is_valid = True
        for item in staging_data:
            if not item.conta_id:
                result.errors.append(f"Lançamento {item.chave_origem_sci} sem conta contábil vinculada.")
                is_valid = False
            if not item.data:
                result.errors.append(f"Lançamento {item.chave_origem_sci} sem data (falha no Date Propagation).")
                is_valid = False
        return is_valid
        
    def transform(self, staging_data: List[SciStagingLancamento], result: ParserResult) -> Dict[str, Any]:
        # Componente 5: Canonical Mapper
        canonical = {
            "contas": {},
            "lancamentos": []
        }
        
        for stg in staging_data:
            if stg.conta_id not in canonical["contas"]:
                canonical["contas"][stg.conta_id] = ContaContabil(
                    codigo_contabil=stg.conta_id,
                    descricao=f"Conta {stg.conta_id}", # Ideal é capturar a desc no Header, guardamos no contexto
                    # Vamos ignorar a falta de descrição completa por hora e delegar à criação se não existir.
                )
                
            lanc = LancamentoContabil(
                data=stg.data,
                historico=stg.historico,
                valor=stg.valor,
                tipo=stg.tipo,
                lote=stg.lote,
                chave_origem_sci=stg.chave_origem_sci,
                conta_contrapartida=stg.conta_contrapartida
            )
            lanc._temp_conta_id = stg.conta_id
            canonical["lancamentos"].append(lanc)
            
        return canonical

    def load(self, canonical_data: Dict[str, Any], importacao: ImportacaoArquivo, db_session: Session) -> None:
        for c in canonical_data["contas"].values():
            c.arquivo_origem = importacao.id
            c.origem_sistema = "EXCEL_SCI"
            db_session.add(c)
            
        db_session.flush() # Gerar IDs das contas ou vincular
        
        for l in canonical_data["lancamentos"]:
            l.arquivo_origem = importacao.id
            l.origem_sistema = "EXCEL_SCI"
            l.conta_contabil = canonical_data["contas"][l._temp_conta_id]
            db_session.add(l)
