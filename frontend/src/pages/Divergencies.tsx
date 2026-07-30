import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { divergenciesApi } from '../api/candidates';

export const Divergencies: React.FC = () => {
  const { data: divergencies, isLoading, error } = useQuery({
    queryKey: ['divergencies'],
    queryFn: divergenciesApi.list
  });

  if (isLoading) return <div style={{ padding: '2rem' }}>Carregando divergências...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Erro ao carregar divergências.</div>;
  if (!divergencies || divergencies.length === 0) return <div style={{ padding: '2rem' }}>Nenhuma divergência encontrada.</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Divergências Bancárias</h2>
      <p style={{ color: '#4b5563', marginBottom: '2rem' }}>Movimentações que não encontraram match ou que foram rejeitadas na revisão.</p>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #d1d5db' }}>
              <th style={{ padding: '1rem', fontWeight: '600', color: '#374151' }}>Data</th>
              <th style={{ padding: '1rem', fontWeight: '600', color: '#374151' }}>Histórico</th>
              <th style={{ padding: '1rem', fontWeight: '600', color: '#374151' }}>Valor</th>
              <th style={{ padding: '1rem', fontWeight: '600', color: '#374151' }}>Motivo (Status)</th>
            </tr>
          </thead>
          <tbody>
            {divergencies.map((div) => (
              <tr key={div.mov_id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                <td style={{ padding: '1rem', color: '#4b5563' }}>{div.data_ocorrencia}</td>
                <td style={{ padding: '1rem', color: '#1f2937' }}>{div.historico}</td>
                <td style={{ padding: '1rem', color: '#1f2937', fontWeight: '500' }}>R$ {div.valor}</td>
                <td style={{ padding: '1rem', color: '#ef4444' }}>{div.motivo}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
