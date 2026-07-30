export enum StatusExecucao {
  CRIADA = "CRIADA",
  ARQUIVOS_ANEXADOS = "ARQUIVOS_ANEXADOS",
  PROCESSANDO = "PROCESSANDO",
  CONCLUIDA = "CONCLUIDA",
  ERRO = "ERRO"
}

export interface Execution {
  id: string;
  status: StatusExecucao;
  matching_profile: string;
  runtime_profile: string;
  hashes_arquivos?: string;
  erro_codigo?: string;
  erro_mensagem?: string;
  erro_stacktrace?: string;
  data_inicio?: string;
  data_fim?: string;
  duracao_ms?: number;
}
