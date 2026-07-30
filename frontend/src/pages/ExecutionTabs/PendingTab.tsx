import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { useAuth } from '../../auth/AuthProvider';

export const PendingTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  const { data: candidates, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'candidates'],
    queryFn: async () => (await api.get(`/executions/${executionId}/candidates`)).data
  });

  const decisionMutation = useMutation({
    mutationFn: async ({ id, action, comment }: { id: string; action: string; comment: string }) => {
      await api.post(`/candidates/${id}/decision`, { action, comment });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'candidates'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'summary'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'conciliations'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'divergencies'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'logs'] });
    }
  });

  if (isLoading) return <div>Carregando pendentes...</div>;
  if (!candidates || candidates.length === 0) return <div>Nenhum candidato pendente para esta execução.</div>;

  return (
    <div>
      {candidates.map((c: any) => (
        <div key={c.id} style={{ border: '1px solid #ddd', padding: '15px', marginBottom: '15px', borderRadius: '8px' }}>
          <h4>Score: {c.score_total.toFixed(2)}</h4>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px' }}>
              <strong>Banco:</strong> {c.movimentacao_original.historico} <br/>
              R$ {c.movimentacao_original.valor}
            </div>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px' }}>
              <strong>ERP:</strong> {c.parcela_original.fornecedor} - Doc {c.parcela_original.documento} <br/>
              R$ {c.parcela_original.valor}
            </div>
          </div>
          {user?.role !== 'AUDITOR' && (
            <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => decisionMutation.mutate({ id: c.id, action: 'APROVAR', comment: 'Aprovado manualmente' })}
                style={{ background: '#28a745', color: 'white', padding: '5px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Aprovar
              </button>
              <button 
                onClick={() => decisionMutation.mutate({ id: c.id, action: 'REJEITAR', comment: 'Rejeitado manualmente' })}
                style={{ background: '#dc3545', color: 'white', padding: '5px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Rejeitar
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
