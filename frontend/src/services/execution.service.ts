import { apiClient } from './api';

export const executionService = {
  list: async () => {
    const res = await apiClient.get('/executions');
    return res.data;
  },
  getById: async (id: string) => {
    const res = await apiClient.get(`/executions/${id}`);
    return res.data;
  },
  getSummary: async (id: string) => {
    const res = await apiClient.get(`/executions/${id}/summary`);
    return res.data;
  },
  getConciliations: async (id: string) => {
    const res = await apiClient.get(`/executions/${id}/conciliations`);
    return res.data;
  },
  getDivergencies: async (id: string) => {
    const res = await apiClient.get(`/executions/${id}/divergencies`);
    return res.data;
  },
  getTimeline: async (id: string) => {
    const res = await apiClient.get(`/executions/${id}/logs`);
    return res.data;
  }
};
