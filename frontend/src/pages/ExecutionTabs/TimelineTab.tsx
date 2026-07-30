import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';

export const TimelineTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'logs'],
    queryFn: async () => (await api.get(`/executions/${executionId}/logs`)).data
  });

  if (isLoading) return <div>Carregando timeline...</div>;
  if (!logs || logs.length === 0) return <div>Nenhum evento registrado nesta execução.</div>;

  return (
    <div>
      {logs.map((log: any, idx: number) => (
        <div key={idx} style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
          <div style={{ minWidth: '150px', color: '#666', fontSize: '14px' }}>
            {new Date(log.timestamp).toLocaleString()}
          </div>
          <div style={{ borderLeft: '2px solid #0070f3', paddingLeft: '15px', paddingBottom: '15px' }}>
            <strong>{log.type.replace(/_/g, ' ')}</strong>
            <p style={{ margin: '5px 0', fontSize: '14px' }}>{log.details}</p>
            {log.score > 0 && <span style={{ fontSize: '12px', background: '#eee', padding: '2px 6px', borderRadius: '4px' }}>Score: {log.score.toFixed(2)}</span>}
          </div>
        </div>
      ))}
    </div>
  );
};
