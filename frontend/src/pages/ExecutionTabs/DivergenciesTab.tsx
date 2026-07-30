import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';

export const DivergenciesTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: divergencies, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'divergencies'],
    queryFn: async () => (await api.get(`/executions/${executionId}/divergencies`)).data
  });

  if (isLoading) return <div>Carregando divergências...</div>;
  if (!divergencies || divergencies.length === 0) return <div>Nenhuma divergência nesta execução.</div>;

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr style={{ background: '#f5f5f5', textAlign: 'left' }}>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Data</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Histórico Bancário</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Valor</th>
          <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Motivo</th>
        </tr>
      </thead>
      <tbody>
        {divergencies.map((d: any) => (
          <tr key={d.mov_id} style={{ borderBottom: '1px solid #eee' }}>
            <td style={{ padding: '10px' }}>{new Date(d.data_ocorrencia).toLocaleDateString()}</td>
            <td style={{ padding: '10px' }}>{d.historico}</td>
            <td style={{ padding: '10px', color: d.valor < 0 ? 'red' : 'green' }}>R$ {d.valor}</td>
            <td style={{ padding: '10px' }}>{d.motivo}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
