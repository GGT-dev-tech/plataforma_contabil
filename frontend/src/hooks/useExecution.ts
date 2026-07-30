import { useQuery } from '@tanstack/react-query';
import { executionService } from '../services/execution.service';

export const useExecutions = () => {
  return useQuery({
    queryKey: ['executions'],
    queryFn: executionService.list
  });
};

export const useExecution = (id: string) => {
  return useQuery({
    queryKey: ['execution', id],
    queryFn: () => executionService.getById(id),
    enabled: !!id
  });
};

export const useSummary = (id: string) => {
  return useQuery({
    queryKey: ['execution', id, 'summary'],
    queryFn: () => executionService.getSummary(id),
    enabled: !!id
  });
};

export const useConciliations = (id: string) => {
  return useQuery({
    queryKey: ['execution', id, 'conciliations'],
    queryFn: () => executionService.getConciliations(id),
    enabled: !!id
  });
};

export const useDivergencies = (id: string) => {
  return useQuery({
    queryKey: ['execution', id, 'divergencies'],
    queryFn: () => executionService.getDivergencies(id),
    enabled: !!id
  });
};

export const useTimeline = (id: string) => {
  return useQuery({
    queryKey: ['execution', id, 'logs'],
    queryFn: () => executionService.getTimeline(id),
    enabled: !!id
  });
};
