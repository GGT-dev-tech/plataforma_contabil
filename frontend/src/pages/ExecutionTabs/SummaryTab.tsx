import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { StatCard } from '../../components/ui/StatCard';
import { Skeleton } from '../../components/ui/Loading';

export const SummaryTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['execution', executionId, 'summary'],
    queryFn: async () => (await api.get(`/executions/${executionId}/summary`)).data
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-destructive p-4">Erro ao carregar resumo da execução.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard 
        title="Total Movimentações" 
        value={data.total_movimentacoes} 
        colorBorder="blue"
      />
      <StatCard 
        title="Aprovados" 
        value={data.total_aprovados} 
        colorBorder="green"
      />
      <StatCard 
        title="Pendentes" 
        value={data.total_pendentes} 
        colorBorder="yellow"
      />
      <StatCard 
        title="Divergências" 
        value={data.total_rejeitados} 
        colorBorder="red"
      />
    </div>
  );
};
