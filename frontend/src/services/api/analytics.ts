import { apiClient as api } from '../api';

export interface DashboardData {
  retencoes: {
    iss: number;
    inss: number;
    ir: number;
    csll: number;
  };
  obras_regime: Array<{
    regime: string;
    quantidade: number;
  }>;
  evolucao: Array<{
    name: string;
    valor: number;
  }>;
}

export const getDashboardData = async (empresaId: string): Promise<DashboardData> => {
  const params = new URLSearchParams();
  if (empresaId) {
    params.append('empresa_id', empresaId);
  }
  
  const response = await api.get(`/analytics/dashboard?${params.toString()}`);
  return response.data;
};
