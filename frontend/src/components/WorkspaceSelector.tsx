import React from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Building2, ChevronDown } from 'lucide-react';

export const WorkspaceSelector: React.FC = () => {
  const { workspaces, activeWorkspaceId, setActiveWorkspaceId, isLoading } = useWorkspace();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-sm animate-pulse">
        <Building2 className="w-4 h-4"/> Carregando...
      </div>
    );
  }

  if (workspaces.length === 0) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
        <Building2 className="w-4 h-4"/> Nenhuma Empresa Encontrada
      </div>
    );
  }

  return (
    <div className="relative group">
      <div className="relative flex items-center bg-white hover:bg-slate-50 border border-slate-300 rounded-lg px-4 py-2 transition-all duration-300 shadow-sm focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500">
        <Building2 className="w-4 h-4 text-primary-600 mr-2" />
        <select
          value={activeWorkspaceId || ''}
          onChange={(e) => setActiveWorkspaceId(e.target.value)}
          className="bg-transparent text-sm font-medium text-slate-800 outline-none cursor-pointer focus:ring-0 min-w-[180px] appearance-none pr-6"
        >
          <option value="" disabled className="text-slate-500">Selecione uma Empresa</option>
          {workspaces.map((ws) => (
            <option key={ws.id} value={ws.id} className="text-slate-800 bg-white">
              {ws.nome_fantasia || ws.razao_social}
            </option>
          ))}
        </select>
        <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 pointer-events-none" />
      </div>
    </div>
  );
};
