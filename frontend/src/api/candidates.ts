import { apiClient } from './client';
import { MatchCandidate, Divergencia } from '../types/candidate';

export const candidatesApi = {
  listPending: async (): Promise<MatchCandidate[]> => {
    const { data } = await apiClient.get<MatchCandidate[]>('/candidates', {
      params: { status: 'PENDENTE_REVISAO' }
    });
    return data;
  },

  decide: async (candidateId: string, action: 'APROVAR' | 'REJEITAR', comment: string) => {
    const { data } = await apiClient.post(`/candidates/${candidateId}/decision`, {
      action,
      comment
    });
    return data;
  }
};

export const divergenciesApi = {
  list: async (): Promise<Divergencia[]> => {
    const { data } = await apiClient.get<Divergencia[]>('/divergencies');
    return data;
  }
};
