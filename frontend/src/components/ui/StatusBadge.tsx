import React from 'react';
import { Badge } from './Badge';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  let variant: 'default' | 'success' | 'warning' | 'destructive' | 'secondary' = 'default';
  
  const s = status.toUpperCase();
  if (s === 'CONCLUIDA' || s === 'APROVADO') variant = 'success';
  else if (s === 'PROCESSANDO' || s === 'PENDENTE_REVISAO') variant = 'warning';
  else if (s === 'REJEITADO_PELO_MOTOR' || s === 'REJEITADO_HUMANO' || s === 'FALHA') variant = 'destructive';
  else if (s === 'CRIADA') variant = 'secondary';

  return <Badge variant={variant}>{status}</Badge>;
};
