import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useExecutions } from '../hooks/useExecution';
import { useAuth } from '../contexts/AuthContext';
import { DataTable } from '../components/ui/DataTable';
import { StatusBadge } from '../components/ui/StatusBadge';
import { PageHeader } from '../components/layout/PageHeader';
import { Loading } from '../components/ui/Loading';
import { EmptyState } from '../components/ui/EmptyState';
import { Plus, ListX, Sparkles } from 'lucide-react';

export const ExecutionsList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: executions, isLoading, error } = useExecutions();

  if (isLoading) return <Loading text="Carregando execuções..." fullScreen />;
  if (error) return <div className="text-red-500 p-4">Erro ao carregar execuções.</div>;

  return (
    <div className="space-y-8 animate-fade-in relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-[80px] -z-10 pointer-events-none"></div>
      
      <PageHeader 
        title="Execuções de Conciliação" 
        description="Gerencie e acompanhe o status de todas as rotinas de conciliação processadas pelo sistema em tempo real."
        action={
          user?.role !== 'AUDITOR' && (
            <button 
              onClick={() => navigate('/executions/new')} 
              className="glass-button-primary flex items-center gap-2 px-6 py-2.5 group"
            >
              <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
              <span className="font-semibold tracking-wide">Nova Execução</span>
              <Sparkles className="w-4 h-4 opacity-50 absolute top-1 right-2" />
            </button>
          )
        }
      />

      {!executions || executions.length === 0 ? (
        <div className="glass-panel rounded-2xl p-8 text-center border border-white/5">
          <EmptyState 
            icon={ListX} 
            title="Nenhuma execução encontrada" 
            description="Você ainda não possui execuções de conciliação. Crie uma nova execução para começar." 
          />
        </div>
      ) : (
        <DataTable 
          data={executions}
          keyExtractor={(exec: any) => exec.id}
          onRowClick={(exec: any) => navigate(`/executions/${exec.id}`)}
          columns={[
            { header: 'ID', accessor: (exec: any) => <span className="font-mono text-xs text-primary-400 bg-primary-900/30 px-2 py-1 rounded border border-primary-500/20 shadow-inner">{exec.id.substring(0, 8)}</span> },
            { header: 'Data Início', accessor: (exec: any) => new Date(exec.data_inicio).toLocaleString() },
            { header: 'Status', accessor: (exec: any) => <StatusBadge status={exec.status} /> }
          ]}
        />
      )}
    </div>
  );
};
