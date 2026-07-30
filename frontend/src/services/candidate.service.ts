import { apiClient } from './api';

export const candidateService = {
  getByExecutionId: async (executionId: string) => {
    const res = await apiClient.get(`/executions/${executionId}/candidates`);
    return res.data;
  },
  decide: async (id: string, action: 'APROVAR' | 'REJEITAR', comment?: string) => {
    const res = await apiClient.post(`/candidates/${id}/decision`, { action, comment });
    return res.data;
  }
};
