import React from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Building2 } from 'lucide-react';

export const WorkspaceSelector: React.FC = () => {
  const { workspaces, activeWorkspaceId, setActiveWorkspaceId, isLoading } = useWorkspace();

  if (isLoading) {
    return <div className="text-sm text-gray-500 animate-pulse flex items-center gap-2"><Building2 className="w-4 h-4"/> Carregando workspaces...</div>;
  }

  if (workspaces.length === 0) {
    return <div className="text-sm text-red-500">Nenhum workspace encontrado</div>;
  }

  return (
    <div className="flex items-center space-x-2 bg-slate-800 rounded-md px-3 py-1.5 border border-slate-700 shadow-sm">
      <Building2 className="w-4 h-4 text-slate-400" />
      <select
        value={activeWorkspaceId || ''}
        onChange={(e) => setActiveWorkspaceId(e.target.value)}
        className="bg-transparent text-sm text-slate-200 outline-none cursor-pointer focus:ring-0 min-w-[150px] appearance-none"
      >
        <option value="" disabled className="text-gray-500">Selecione uma Empresa</option>
        {workspaces.map((ws) => (
          <option key={ws.id} value={ws.id} className="bg-slate-800 text-slate-200">
            {ws.nome_fantasia || ws.razao_social}
          </option>
        ))}
      </select>
    </div>
  );
};
