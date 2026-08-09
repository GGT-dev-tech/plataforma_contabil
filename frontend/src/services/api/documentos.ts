import { apiClient as api } from '../api';

export interface DocumentoFiscal {
  id: string;
  empresa_id?: string;
  obra_id?: string;
  tipo: string;
  natureza_operacao: string;
  status: string;
  numero?: string;
  serie?: string;
  chave_acesso?: string;
  data_emissao?: string;
  data_entrada?: string;
  emitente_cnpj_cpf?: string;
  emitente_nome?: string;
  emitente_municipio_nome?: string;
  valor_bruto: number;
  valor_desconto: number;
  iss_valor: number;
  iss_retido: boolean;
  inss_valor: number;
  inss_retido: boolean;
  ir_valor: number;
  ir_retido: boolean;
  pis_valor: number;
  cofins_valor: number;
  csll_valor: number;
  total_retencoes: number;
  valor_liquido_pagar: number;
  importado_via?: string;
  created_at?: string;
}

export interface LancamentoContabil {
  partida: string;
  conta: string;
  descricao_conta: string;
  valor: number;
  historico: string;
}

export const getDocumentos = async (empresaId?: string, obraId?: string, status?: string): Promise<DocumentoFiscal[]> => {
  const params = new URLSearchParams();
  if (empresaId) params.append('empresa_id', empresaId);
  if (obraId) params.append('obra_id', obraId);
  if (status) params.append('status', status);
  
  const response = await api.get(`/documentos-fiscais?${params.toString()}`);
  return response.data;
};

export const getDocumento = async (id: string): Promise<DocumentoFiscal> => {
  const response = await api.get(`/documentos-fiscais/${id}`);
  return response.data;
};

export const vincularObra = async (id: string, obraId: string): Promise<DocumentoFiscal> => {
  const response = await api.patch(`/documentos-fiscais/${id}/vincular-obra`, { obra_id: obraId });
  return response.data;
};

export const calcularRetencoes = async (id: string, payload: any): Promise<{ documento: DocumentoFiscal, justificativas: string[] }> => {
  const response = await api.post(`/documentos-fiscais/${id}/calcular-retencoes`, payload);
  return { documento: response.data, justificativas: response.data.justificativas };
};

export const gerarLancamentos = async (id: string, contaBancaria?: string): Promise<{ mensagem: string, lote: string, lancamentos: LancamentoContabil[] }> => {
  const params = new URLSearchParams();
  if (contaBancaria) params.append('conta_bancaria', contaBancaria);
  
  const response = await api.post(`/documentos-fiscais/${id}/gerar-lancamentos?${params.toString()}`);
  return response.data;
};

export const sincronizarDocumentos = async (obraId: string, erpName: string = 'sienge'): Promise<{ novos_documentos_importados: number }> => {
  const params = new URLSearchParams();
  params.append('obra_id', obraId);
  params.append('erp_name', erpName);
  
  const response = await api.post(`/sincronizacao/documentos?${params.toString()}`);
  return response.data;
};
