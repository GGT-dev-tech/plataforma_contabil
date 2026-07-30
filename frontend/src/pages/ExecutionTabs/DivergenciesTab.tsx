import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { DataTable } from '../../components/ui/DataTable';
import { EmptyState } from '../../components/ui/EmptyState';
import { AlertTriangle } from 'lucide-react';
import { Loading } from '../../components/ui/Loading';

export const DivergenciesTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: divergencies, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'divergencies'],
    queryFn: async () => (await api.get(`/executions/${executionId}/divergencies`)).data
  });

  if (isLoading) {
    return <Loading text="Carregando divergências..." />;
  }

  if (!divergencies || divergencies.length === 0) {
    return (
      <EmptyState 
        icon={AlertTriangle}
        title="Nenhuma divergência encontrada"
        description="Todas as movimentações desta execução foram conciliadas com sucesso."
      />
    );
  }

  const columns = [
    { 
      header: 'Data Ocorrência', 
      accessor: (d: any) => new Date(d.data_ocorrencia).toLocaleDateString() 
    },
    { 
      header: 'Histórico Bancário', 
      accessor: 'historico' 
    },
    { 
      header: 'Valor', 
      accessor: (d: any) => (
        <span className={d.valor < 0 ? 'text-red-500 font-medium' : 'text-green-500 font-medium'}>
          R$ {parseFloat(d.valor).toFixed(2)}
        </span>
      )
    },
    { 
      header: 'Motivo', 
      accessor: (d: any) => (
        <span className="text-sm bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 px-2 py-1 rounded">
          {d.motivo}
        </span>
      )
    }
  ];

  return (
    <div className="bg-white/30 dark:bg-gray-900/30 rounded-xl overflow-hidden">
      <DataTable 
        data={divergencies} 
        columns={columns} 
        keyExtractor={(d) => d.mov_id}
      />
    </div>
  );
};
