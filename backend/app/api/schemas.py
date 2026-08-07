from pydantic import BaseModel, UUID4, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Regras e Explicações
class RuleResultSchema(BaseModel):
    regra: str
    score: float
    peso: float
    justificativa: str

# API Decision
class DecisionRequest(BaseModel):
    action: str = Field(..., description="APROVAR ou REJEITAR")
    comment: Optional[str] = None
    reviewer: str = "Automated Reviewer"

# Entidades Resposta
class MatchCandidateSchema(BaseModel):
    id: UUID4
    execucao_id: UUID4
    movimentacao_id: UUID4
    parcela_id: Optional[UUID4]
    score_total: float
    status: str
    motivo_descarte: Optional[str]
    regras: List[dict] = []
    
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    decision_comment: Optional[str] = None

class ConciliacaoSchema(BaseModel):
    id: UUID4
    status: str
    tipo_match: str
    score_match: float
    data_criacao: datetime
    matching_profile: Optional[str] = None
    explainability_version: Optional[str] = None
    explicacoes: List[RuleResultSchema] = []

class ExecucaoPipelineSchema(BaseModel):
    id: UUID4
    status: str
    matching_profile: str
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    duracao_ms: Optional[float] = None
    hashes_arquivos: Optional[dict] = None

class DivergenciaSchema(BaseModel):
    mov_id: UUID4
    historico: str
    valor: Decimal
    data_ocorrencia: datetime
    motivo: str

from datetime import date

class StagingUpdateSchema(BaseModel):
    data: Optional[date] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    entidade_nome: Optional[str] = None
    cnpj_cpf: Optional[str] = None
    categoria: Optional[str] = None
    conta_origem: Optional[str] = None
    conta_destino: Optional[str] = None
    forma_pagamento: Optional[str] = None
