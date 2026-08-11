import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { EmptyState } from '../../components/ui/EmptyState';
import { Clock, Activity, CheckCircle2, XCircle } from 'lucide-react';
import { Loading } from '../../components/ui/Loading';

export const TimelineTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'logs'],
    queryFn: async () => (await api.get(`/executions/${executionId}/logs`)).data
  });

  if (isLoading) {
    return <Loading text="Carregando timeline..." />;
  }

  if (!logs || logs.length === 0) {
    return (
      <EmptyState 
        icon={Clock}
        title="Timeline Vazia"
        description="Nenhum evento foi registrado para esta execução ainda."
      />
    );
  }

  const getIcon = (status: string) => {
    if (status.includes('APROVADO')) return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
    if (status.includes('REJEITADO')) return <XCircle className="w-5 h-5 text-red-600" />;
    return <Activity className="w-5 h-5 text-primary-600" />;
  };

  return (
    <div className="relative border-l border-slate-200 ml-3 md:ml-6 space-y-8 py-4">
      {logs.map((log: any, idx: number) => (
        <div key={idx} className="relative pl-8 md:pl-10">
          <span className="absolute -left-3.5 flex items-center justify-center w-7 h-7 bg-white rounded-full ring-4 ring-slate-100 border border-slate-300 shadow-sm">
            {getIcon(log.status)}
          </span>
          
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1">
            <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
              {log.type.replace(/_/g, ' ')}
            </h3>
            <time className="block mb-2 sm:mb-0 text-xs font-semibold text-slate-500">
              {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Sem data'}
            </time>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm mt-2">
            <p className="text-sm text-slate-600">
              {log.details}
            </p>
            {log.score > 0 && (
              <div className="mt-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary-50 text-primary-700 border border-primary-200">
                Score: {log.score.toFixed(2)}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
