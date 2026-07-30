import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';

export const SummaryTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['execution', executionId, 'summary'],
    queryFn: async () => (await api.get(`/executions/${executionId}/summary`)).data
  });

  if (isLoading) return <div>Carregando resumo...</div>;
  if (error) return <div>Erro ao carregar resumo</div>;

  return (
    <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', minWidth: '200px' }}>
        <h3>Total Movimentações</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.total_movimentacoes}</p>
      </div>
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', minWidth: '200px', borderLeft: '5px solid #28a745' }}>
        <h3>Aprovados</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.total_aprovados}</p>
      </div>
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', minWidth: '200px', borderLeft: '5px solid #ffc107' }}>
        <h3>Pendentes</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.total_pendentes}</p>
      </div>
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', minWidth: '200px', borderLeft: '5px solid #dc3545' }}>
        <h3>Rejeitados/Divergentes</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.total_rejeitados}</p>
      </div>
    </div>
  );
};
