import React from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Building2, ChevronDown } from 'lucide-react';

export const WorkspaceSelector: React.FC = () => {
  const { workspaces, activeWorkspaceId, setActiveWorkspaceId, isLoading } = useWorkspace();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 text-sm animate-pulse">
        <Building2 className="w-4 h-4"/> Carregando...
      </div>
    );
  }

  if (workspaces.length === 0) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
        <Building2 className="w-4 h-4"/> Nenhuma Empresa Encontrada
      </div>
    );
  }

  return (
    <div className="relative group">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-500/20 to-accent-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition duration-500"></div>
      <div className="relative flex items-center bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl px-4 py-2 transition-all duration-300">
        <Building2 className="w-4 h-4 text-primary-400 mr-2" />
        <select
          value={activeWorkspaceId || ''}
          onChange={(e) => setActiveWorkspaceId(e.target.value)}
          className="bg-transparent text-sm font-medium text-white outline-none cursor-pointer focus:ring-0 min-w-[180px] appearance-none pr-6"
        >
          <option value="" disabled className="bg-gray-900 text-gray-500">Selecione uma Empresa</option>
          {workspaces.map((ws) => (
            <option key={ws.id} value={ws.id} className="bg-gray-900 text-gray-200">
              {ws.nome_fantasia || ws.razao_social}
            </option>
          ))}
        </select>
        <ChevronDown className="w-4 h-4 text-gray-400 absolute right-4 pointer-events-none" />
      </div>
    </div>
  );
};
