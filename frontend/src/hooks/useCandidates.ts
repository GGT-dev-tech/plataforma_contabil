import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidateService } from '../services/candidate.service';

export const useCandidates = (executionId: string) => {
  return useQuery({
    queryKey: ['execution', executionId, 'candidates'],
    queryFn: () => candidateService.getByExecutionId(executionId),
    enabled: !!executionId
  });
};

export const useCandidateDecision = (executionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, action, comment }: { id: string; action: 'APROVAR' | 'REJEITAR'; comment?: string }) => 
      candidateService.decide(id, action, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['execution', executionId] });
    }
  });
};
