import { apiClient as api } from '../api';

export interface Obra {
  id: string;
  empresa_id: string;
  nome: string;
  codigo_interno?: string;
  codigo_cno?: string;
  endereco_obra?: string;
  municipio_ibge?: string;
  municipio_nome?: string;
  uf?: string;
  tipo: string;
  status: string;
  regime_tributario: string;
  patrimonio_afetacao: boolean;
  data_inicio?: string;
  data_entrega_prevista?: string;
  data_conclusao_real?: string;
  orcamento_total?: number;
  receita_contratada_total?: number;
  custo_incorrido_total: number;
  percentual_avanco_fisico: number;
}

export const getObras = async (empresaId?: string, status?: string): Promise<Obra[]> => {
  const params = new URLSearchParams();
  if (empresaId) params.append('empresa_id', empresaId);
  if (status) params.append('status', status);
  
  const response = await api.get(`/obras?${params.toString()}`);
  return response.data;
};

export const getObra = async (id: string): Promise<Obra> => {
  const response = await api.get(`/obras/${id}`);
  return response.data;
};

export const createObra = async (data: Partial<Obra>): Promise<Obra> => {
  const response = await api.post('/obras', data);
  return response.data;
};

export const updateObra = async (id: string, data: Partial<Obra>): Promise<Obra> => {
  const response = await api.put(`/obras/${id}`, data);
  return response.data;
};

export const atualizarAvancoFisico = async (id: string, percentual: number, custoIncorrido?: number): Promise<Obra> => {
  const params = new URLSearchParams();
  params.append('percentual', percentual.toString());
  if (custoIncorrido !== undefined) {
    params.append('custo_incorrido', custoIncorrido.toString());
  }
  
  const response = await api.patch(`/obras/${id}/avanco?${params.toString()}`);
  return response.data;
};
