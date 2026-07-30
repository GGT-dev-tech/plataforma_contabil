from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from app.models.domain import TipoMovimentacao, TipoArquivo, StatusConciliacao, TipoMatch

class AuditableSchema(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    origem_sistema: Optional[str] = None
    arquivo_origem: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)

class FornecedorResponse(AuditableSchema):
    cnpj_cpf: str
    nome: str
    nome_normalizado: str

class DespesaResponse(AuditableSchema):
    fornecedor_id: UUID
    projeto_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None
    valor_total: Decimal
    data_emissao: date
    id_uuid_origem: str

class ParcelaDespesaResponse(AuditableSchema):
    despesa_id: UUID
    numero_parcela: int
    valor: Decimal
    data_vencimento: date
    data_pagamento_esperada: Optional[date] = None
    id_parcela_origem: str

class PagamentoResponse(AuditableSchema):
    parcela_id: UUID
    movimentacao_id: Optional[UUID] = None
    valor_pago: Decimal
    juros: Decimal
    desconto: Decimal
    data_pagamento: date

class MovimentacaoBancariaResponse(AuditableSchema):
    extrato_id: UUID
    data: date
    historico: str
    descricao_original: str
    valor: Decimal
    tipo: TipoMovimentacao
    codigo_cp: str
    linha_origem: int

class LancamentoContabilResponse(AuditableSchema):
    conta_contabil_id: UUID
    data: date
    historico: str
    valor: Decimal
    tipo: TipoMovimentacao
    lote: str
    chave_origem_sci: str
    conta_contrapartida: str

class ConciliacaoResponse(AuditableSchema):
    status: StatusConciliacao
    tipo_match: TipoMatch
    score_match: int
    regra_utilizada: str
    aprovado_por: Optional[str] = None
    data_aprovacao: Optional[date] = None

class ConciliacaoItemResponse(AuditableSchema):
    conciliacao_id: UUID
    parcela_id: Optional[UUID] = None
    movimentacao_id: Optional[UUID] = None
    lancamento_id: Optional[UUID] = None
