import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useExecutions } from '../hooks/useExecution';
import { useAuth } from '../auth/AuthProvider';
import { Button } from '../components/ui/Button';
import { DataTable } from '../components/ui/DataTable';
import { StatusBadge } from '../components/ui/StatusBadge';
import { PageHeader } from '../components/layout/PageHeader';
import { Loading } from '../components/ui/Loading';
import { EmptyState } from '../components/ui/EmptyState';
import { Plus, ListX } from 'lucide-react';

export const ExecutionsList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: executions, isLoading, error } = useExecutions();

  if (isLoading) return <Loading text="Carregando execuções..." fullScreen />;
  if (error) return <div className="text-red-500 p-4">Erro ao carregar execuções.</div>;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Execuções de Conciliação" 
        description="Gerencie e acompanhe o status de todas as rotinas de conciliação processadas pelo sistema."
        action={
          user?.role !== 'AUDITOR' && (
            <Button onClick={() => navigate('/executions/new')} leftIcon={<Plus className="w-4 h-4" />}>
              Nova Execução
            </Button>
          )
        }
      />

      {!executions || executions.length === 0 ? (
        <EmptyState 
          icon={ListX} 
          title="Nenhuma execução encontrada" 
          description="Você ainda não possui execuções de conciliação. Crie uma nova execução para começar." 
        />
      ) : (
        <DataTable 
          data={executions}
          keyExtractor={(exec: any) => exec.id}
          onRowClick={(exec: any) => navigate(`/executions/${exec.id}`)}
          columns={[
            { header: 'ID', accessor: (exec: any) => <span className="font-mono text-xs">{exec.id.substring(0, 8)}...</span> },
            { header: 'Data Início', accessor: (exec: any) => new Date(exec.data_inicio).toLocaleString() },
            { header: 'Status', accessor: (exec: any) => <StatusBadge status={exec.status} /> }
          ]}
        />
      )}
    </div>
  );
};
