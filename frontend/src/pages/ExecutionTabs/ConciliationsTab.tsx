import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';

export const ConciliationsTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: conciliations, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'conciliations'],
    queryFn: async () => (await api.get(`/executions/${executionId}/conciliations`)).data
  });

  if (isLoading) return <div>Carregando conciliações...</div>;
  if (!conciliations || conciliations.length === 0) return <div>Nenhuma conciliação efetuada nesta execução.</div>;

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr style={{ background: '#f5f5f5', textAlign: 'left' }}>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>ID</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Movimentação</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Parcela</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Score</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Aprovado Por</th>
        </tr>
      </thead>
      <tbody>
        {conciliations.map((c: any) => (
          <tr key={c.conciliacao_id} style={{ borderBottom: '1px solid #eee' }}>
            <td style={{ padding: '10px' }}>{c.conciliacao_id.substring(0,8)}</td>
            <td style={{ padding: '10px' }}>{c.movimentacao.historico} (R$ {c.movimentacao.valor})</td>
            <td style={{ padding: '10px' }}>{c.parcela?.fornecedor} (R$ {c.parcela?.valor})</td>
            <td style={{ padding: '10px' }}>{c.score.toFixed(2)}</td>
            <td style={{ padding: '10px' }}>{c.aprovado_por || 'SYSTEM'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
