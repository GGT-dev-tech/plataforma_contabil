import React from 'react';
import { NavLink } from 'react-router-dom';
import { Settings, Landmark, FileSpreadsheet, CheckCheck, Sparkles, Building2, BarChart3, ReceiptText } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItemClass = ({ isActive }: { isActive: boolean }) => `
    flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 font-medium text-sm my-1 relative
    ${isActive 
      ? 'bg-primary-50 text-primary-700 font-semibold' 
      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}
  `;

  return (
    <aside className="w-full h-full bg-white rounded-none sm:rounded-xl flex flex-col flex-shrink-0 border border-slate-200 shadow-sm relative">
      
      <div className="h-16 flex items-center px-6 border-b border-slate-100 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-sm">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-slate-800 tracking-tight">
            Plataforma<span className="text-primary-600">.</span>
          </h1>
        </div>
      </div>
      
      <nav className="flex-1 px-4 py-6 space-y-6 overflow-y-auto relative z-10 custom-scrollbar">
        
        <div>
          <NavLink to="/dashboard" className={navItemClass}>
            <Building2 className="w-4 h-4 mr-3" />
            Visão Geral
          </NavLink>
        </div>
        
        <div>
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            Financeiro
          </p>
          <NavLink to="/receitas-despesas" className={navItemClass}>
            <Landmark className="w-4 h-4 mr-3" />
            DRE Gerencial
          </NavLink>
          <NavLink to="/executions" className={navItemClass}>
            <CheckCheck className="w-4 h-4 mr-3" />
            Conciliação Bancária
          </NavLink>
        </div>

        <div>
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            Fiscal
          </p>
          <NavLink to="/documentos-fiscais" className={navItemClass}>
            <ReceiptText className="w-4 h-4 mr-3" />
            Apurações Mensais
          </NavLink>
          <NavLink to="/crm" className={navItemClass}>
            <BarChart3 className="w-4 h-4 mr-3" />
            Regimes Tributários
          </NavLink>
        </div>

        <div>
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            Contábil
          </p>
          <NavLink to="/exportacao-contabil" className={navItemClass}>
            <FileSpreadsheet className="w-4 h-4 mr-3" />
            Exportação SPED
          </NavLink>
        </div>
      </nav>
      
      <div className="p-4 border-t border-slate-100 relative z-10 flex flex-col gap-1">
        <NavLink to="/settings" className={navItemClass}>
          <Settings className="w-4 h-4 mr-3" />
          Configurações
        </NavLink>
        <NavLink to="/ui" className={navItemClass}>
          <Sparkles className="w-4 h-4 mr-3 text-accent-500" />
          Componentes UI
        </NavLink>
      </div>
    </aside>
  );
};
