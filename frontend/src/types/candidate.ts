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
  movimentacao_id: string;
  parcela_id: string;
  score_total: number;
  status: StatusCandidato;
  regras: RuleExplanation[];
  
  movimentacao_original: {
    historico: string;
    valor: string;
    data: string | null;
  };
  
  parcela_original: {
    documento: string;
    fornecedor: string;
    valor: string;
    data_vencimento: string | null;
  };
}

export interface Divergencia {
  mov_id: string;
  historico: string;
  valor: number;
  data_ocorrencia: string;
  motivo: string;
}
