import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { StatCard } from '../../components/ui/StatCard';
import { Skeleton } from '../../components/ui/Loading';
import { Landmark, Receipt, CircleDollarSign, TrendingDown } from 'lucide-react';

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
    <div className="space-y-8">
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

      {data.tax_summary && (
        <div className="bg-white/50 dark:bg-gray-800/50 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Landmark className="w-5 h-5 text-indigo-500" />
            Resumo Fiscal Pré-Calculado
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 mb-1 flex items-center gap-1"><CircleDollarSign className="w-4 h-4"/> Faturamento Estimado</p>
              <p className="text-xl font-bold">R$ {parseFloat(data.tax_summary.total_faturamento || '0').toFixed(2)}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 mb-1 flex items-center gap-1"><TrendingDown className="w-4 h-4"/> Despesas Totais</p>
              <p className="text-xl font-bold">R$ {parseFloat(data.tax_summary.total_despesas || '0').toFixed(2)}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 mb-1 flex items-center gap-1"><Receipt className="w-4 h-4"/> Impostos Devidos</p>
              <p className="text-xl font-bold text-red-600 dark:text-red-400">R$ {parseFloat(data.tax_summary.impostos_devidos || '0').toFixed(2)}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 mb-1 flex items-center gap-1"><Receipt className="w-4 h-4"/> Impostos Retidos</p>
              <p className="text-xl font-bold text-yellow-600 dark:text-yellow-400">R$ {parseFloat(data.tax_summary.impostos_retidos || '0').toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
