import React from 'react';
import { useParams } from 'react-router-dom';
import { useExecution } from '../hooks/useExecution';
import { SummaryTab } from './ExecutionTabs/SummaryTab';
import { PendingTab } from './ExecutionTabs/PendingTab';
import { ConciliationsTab } from './ExecutionTabs/ConciliationsTab';
import { DivergenciesTab } from './ExecutionTabs/DivergenciesTab';
import { TimelineTab } from './ExecutionTabs/TimelineTab';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs } from '../components/ui/Tabs';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';
import { Loading } from '../components/ui/Loading';

export const ExecutionView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: execution, isLoading, error } = useExecution(id!);

  if (isLoading) return <Loading text="Carregando execução..." fullScreen />;
  if (error || !execution) return <div className="text-red-500 p-4">Erro ao carregar a execução.</div>;

  const tabItems = [
    { id: 'summary', label: 'Resumo', content: <SummaryTab executionId={id!} /> },
    { id: 'pending', label: 'Pendentes', content: <PendingTab executionId={id!} /> },
    { id: 'conciliations', label: 'Conciliados', content: <ConciliationsTab executionId={id!} /> },
    { id: 'divergencies', label: 'Divergências', content: <DivergenciesTab executionId={id!} /> },
    { id: 'timeline', label: 'Timeline', content: <TimelineTab executionId={id!} /> }
  ];

  return (
    <div className="space-y-6">
      <Breadcrumb 
        items={[
          { label: 'Execuções', href: '/executions' },
          { label: `Execução ${execution.id.substring(0, 8)}` }
        ]} 
      />

      <PageHeader 
        title={`Execução: ${execution.id.substring(0, 8)}`}
        action={<StatusBadge status={execution.status} />}
      />

      <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-md rounded-2xl border border-gray-200/50 dark:border-gray-700/50 p-6 shadow-sm">
        <Tabs tabs={tabItems} defaultTab="summary" />
      </div>
    </div>
  );
};
