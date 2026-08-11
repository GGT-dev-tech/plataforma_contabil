export enum StatusCandidato {
  PENDENTE_REVISAO = "PENDENTE_REVISAO",
  APROVADO = "APROVADO",
  REJEITADO_PELO_MOTOR = "REJEITADO_PELO_MOTOR"
}

export interface RuleExplanation {
  nome: string;
  score: number;
  peso: number;
  confidence: number;
  justificativa: string;
}

export interface MatchCandidate {
  id: string;
  execucao_id: string;
  movimentacao_financeira_id: string;
  titulo_id: string | null;
  lancamento_cabecalho_id: string | null;
  score_total: number;
  status: StatusCandidato;
  regras: RuleExplanation[];

  transacao_original: {
    historico: string;
    valor: string;
    data: string | null;
  } | null;

  titulo_original: {
    descricao: string;
    fornecedor: string;
    valor: string;
    data_vencimento: string | null;
  } | null;

  lancamento_original: {
    historico: string;
    numero_lote: string;
    total_partidas: number;
  } | null;
}

export interface Conciliacao {
  conciliacao_id: string;
  status: string;
  aprovado_por: string | null;
  data_conciliacao: string | null;
  score: number;
  transacao: {
    historico: string;
    valor: string;
    data: string | null;
  } | null;
  titulo: {
    descricao: string;
    fornecedor: string;
    valor: string;
  } | null;
  lancamento: {
    historico: string;
    numero_lote: string;
  } | null;
}

export interface Divergencia {
  mov_id: string;
  historico: string;
  valor: number;
  data_ocorrencia: string;
  motivo: string;
}
