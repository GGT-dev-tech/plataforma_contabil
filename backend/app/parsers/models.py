from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ParserMetrics(BaseModel):
    linhas_lidas: int = 0
    linhas_validas: int = 0
    linhas_descartadas: int = 0
    erros: int = 0
    tempo_execucao_ms: int = 0
    versao_parser: str = "1.0"
    hash_arquivo: str = ""
    estatisticas_especificas: Dict[str, Any] = {}

class ParserResult(BaseModel):
    metadata: Dict[str, Any] = {}
    staging_records: List[Any] = []
    warnings: List[str] = []
    errors: List[str] = []
    metrics: ParserMetrics = ParserMetrics()

class ParserReport(BaseModel):
    """Relatório estruturado gerado ao final de qualquer importação"""
    arquivo: str
    status: str
    metrics: ParserMetrics
    warnings: List[str]
    errors: List[str]
    timestamp: datetime = datetime.now()
