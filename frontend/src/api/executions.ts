import { apiClient } from './client';
import { Execution } from '../types/execution';

export const executionsApi = {
  create: async (): Promise<Execution> => {
    const { data } = await apiClient.post<Execution>('/executions');
    return data;
  },

  uploadFiles: async (executionId: string, despesas: File, razao: File, extrato: File) => {
    const formData = new FormData();
    formData.append('despesas', despesas);
    formData.append('razao', razao);
    formData.append('extrato', extrato);
    
    const { data } = await apiClient.post(`/executions/${executionId}/files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  run: async (executionId: string) => {
    const { data } = await apiClient.post(`/executions/${executionId}/run`);
    return data;
  }
};
