import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient as api } from '../../services/api';
import { useAuth } from '../../auth/AuthProvider';
import { GlassCard } from '../../components/ui/GlassCard';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CheckCircle2, XCircle } from 'lucide-react';
import { Loading } from '../../components/ui/Loading';

export const PendingTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  const { data: candidates, isLoading } = useQuery({
    queryKey: ['execution', executionId, 'candidates'],
    queryFn: async () => (await api.get(`/executions/${executionId}/candidates`)).data
  });

  const decisionMutation = useMutation({
    mutationFn: async ({ id, action, comment }: { id: string; action: string; comment: string }) => {
      await api.post(`/candidates/${id}/decision`, { action, comment });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'candidates'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'summary'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'conciliations'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'divergencies'] });
      queryClient.invalidateQueries({ queryKey: ['execution', executionId, 'logs'] });
    }
  });

  if (isLoading) {
    return <Loading text="Carregando pendentes..." />;
  }

  if (!candidates || candidates.length === 0) {
    return (
      <EmptyState 
        icon={CheckCircle2}
        title="Tudo certo por aqui!"
        description="Nenhum candidato pendente de revisão para esta execução."
      />
    );
  }

  return (
    <div className="space-y-6">
      {candidates.map((c: any) => (
        <GlassCard key={c.id} className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h4 className="text-lg font-semibold flex items-center gap-2">
              Sugestão do Motor
              <Badge variant={c.score_total > 80 ? 'success' : 'warning'}>
                Score: {c.score_total.toFixed(2)}
              </Badge>
            </h4>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white/50 dark:bg-gray-900/50 p-4 rounded-xl border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Banco Original</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">{c.movimentacao_original.historico}</p>
              <p className="text-lg font-bold mt-2">R$ {parseFloat(c.movimentacao_original.valor).toFixed(2)}</p>
            </div>
            
            <div className="bg-white/50 dark:bg-gray-900/50 p-4 rounded-xl border border-gray-100 dark:border-gray-800">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">ERP (Parcela Sugerida)</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">{c.parcela_original.fornecedor} - Doc {c.parcela_original.documento}</p>
              <p className="text-lg font-bold mt-2">R$ {parseFloat(c.parcela_original.valor).toFixed(2)}</p>
            </div>
          </div>

          {user?.role !== 'AUDITOR' && (
            <div className="mt-6 flex gap-3 border-t border-gray-200 dark:border-gray-700/50 pt-4">
              <Button 
                onClick={() => decisionMutation.mutate({ id: c.id, action: 'APROVAR', comment: 'Aprovado manualmente' })}
                variant="default"
                className="bg-green-600 hover:bg-green-700 text-white"
                leftIcon={<CheckCircle2 className="w-4 h-4" />}
                isLoading={decisionMutation.isPending && decisionMutation.variables?.id === c.id && decisionMutation.variables?.action === 'APROVAR'}
              >
                Aprovar Sugestão
              </Button>
              <Button 
                onClick={() => decisionMutation.mutate({ id: c.id, action: 'REJEITAR', comment: 'Rejeitado manualmente' })}
                variant="destructive"
                leftIcon={<XCircle className="w-4 h-4" />}
                isLoading={decisionMutation.isPending && decisionMutation.variables?.id === c.id && decisionMutation.variables?.action === 'REJEITAR'}
              >
                Rejeitar Sugestão
              </Button>
            </div>
          )}
        </GlassCard>
      ))}
    </div>
  );
};
