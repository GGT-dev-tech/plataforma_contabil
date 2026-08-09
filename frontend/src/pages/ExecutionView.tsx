import React from 'react';
import { useParams } from 'react-router-dom';
import { useExecution } from '../hooks/useExecution';
import { SummaryTab } from './ExecutionTabs/SummaryTab';
import { PendingTab } from './ExecutionTabs/PendingTab';
import { ConciliationsTab } from './ExecutionTabs/ConciliationsTab';
import { DivergenciesTab } from './ExecutionTabs/DivergenciesTab';
import { TimelineTab } from './ExecutionTabs/TimelineTab';
import { ExportTab } from './ExecutionTabs/ExportTab';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';
import { Loading } from '../components/ui/Loading';

export const ExecutionView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: execution, isLoading, error } = useExecution(id!);

  if (isLoading) return <Loading text="Carregando execução..." fullScreen />;
  if (error || !execution) return <div className="text-red-500 p-4">Erro ao carregar a execução.</div>;

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
        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="summary">Resumo</TabsTrigger>
            <TabsTrigger value="pending">Pendentes</TabsTrigger>
            <TabsTrigger value="conciliations">Conciliados</TabsTrigger>
            <TabsTrigger value="divergencies">Divergências</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
            <TabsTrigger value="export">Exportação</TabsTrigger>
          </TabsList>
          
          <TabsContent value="summary"><SummaryTab executionId={id!} /></TabsContent>
          <TabsContent value="pending"><PendingTab executionId={id!} /></TabsContent>
          <TabsContent value="conciliations"><ConciliationsTab executionId={id!} /></TabsContent>
          <TabsContent value="divergencies"><DivergenciesTab executionId={id!} /></TabsContent>
          <TabsContent value="timeline"><TimelineTab executionId={id!} /></TabsContent>
          <TabsContent value="export"><ExportTab executionId={id!} /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
