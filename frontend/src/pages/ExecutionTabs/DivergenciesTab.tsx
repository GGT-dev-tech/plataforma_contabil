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
        <span className={d.valor < 0 ? 'text-red-600 font-semibold' : 'text-emerald-600 font-semibold'}>
          R$ {parseFloat(d.valor).toFixed(2)}
        </span>
      )
    },
    { 
      header: 'Motivo', 
      accessor: (d: any) => (
        <span className="text-xs font-semibold bg-red-50 text-red-700 border border-red-200 px-2.5 py-1 rounded-md">
          {d.motivo}
        </span>
      )
    }
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <DataTable 
        data={divergencies} 
        columns={columns} 
        keyExtractor={(d) => d.mov_id}
      />
    </div>
  );
};
