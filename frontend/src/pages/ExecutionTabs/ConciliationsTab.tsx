import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { DataTable } from '../../components/ui/DataTable';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CheckCircle2 } from 'lucide-react';
import { Loading } from '../../components/ui/Loading';

export const ConciliationsTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: conciliations, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'conciliations'],
    queryFn: async () => (await api.get(`/executions/${executionId}/conciliations`)).data
  });

  if (isLoading) {
    return <Loading text="Carregando conciliações..." />;
  }

  if (!conciliations || conciliations.length === 0) {
    return (
      <EmptyState 
        icon={CheckCircle2}
        title="Nenhuma conciliação efetuada"
        description="Esta execução ainda não possui conciliações aprovadas."
      />
    );
  }

  const columns = [
    { 
      header: 'ID', 
      accessor: (c: any) => c.conciliacao_id.substring(0, 8) 
    },
    { 
      header: 'Movimentação Bancária', 
      accessor: (c: any) => (
        <div>
          <p className="font-medium">{c.movimentacao.historico}</p>
          <p className="text-sm text-gray-500">R$ {parseFloat(c.movimentacao.valor).toFixed(2)}</p>
        </div>
      ) 
    },
    { 
      header: 'Parcela ERP', 
      accessor: (c: any) => (
        <div>
          <p className="font-medium">{c.parcela?.fornecedor || 'N/A'}</p>
          <p className="text-sm text-gray-500">R$ {c.parcela?.valor ? parseFloat(c.parcela.valor).toFixed(2) : '0.00'}</p>
        </div>
      ) 
    },
    { 
      header: 'Score', 
      accessor: (c: any) => c.score.toFixed(2) 
    },
    { 
      header: 'Aprovado Por', 
      accessor: (c: any) => (
        <span className="text-sm font-medium text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-300 px-2 py-1 rounded-md">
          {c.aprovado_por || 'SYSTEM'}
        </span>
      )
    },
    {
      header: 'Status',
      accessor: (c: any) => <StatusBadge status={c.status} />
    }
  ];

  return (
    <div className="bg-white/30 dark:bg-gray-900/30 rounded-xl overflow-hidden">
      <DataTable 
        data={conciliations} 
        columns={columns} 
        keyExtractor={(c) => c.conciliacao_id}
      />
    </div>
  );
};
