import React from 'react';
import { NavLink } from 'react-router-dom';
import { Settings, Landmark, FileSpreadsheet, CheckCheck, Sparkles, Building2, BarChart3, ReceiptText } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItemClass = ({ isActive }: { isActive: boolean }) => `
    flex items-center px-4 py-3 rounded-xl transition-all duration-300 group font-medium text-sm my-1 relative overflow-hidden
    ${isActive 
      ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30 shadow-[inset_0_0_12px_rgba(99,102,241,0.1)]' 
      : 'text-gray-400 hover:bg-white/5 hover:text-gray-200 border border-transparent'}
  `;

  return (
    <aside className="w-full h-full glass-panel rounded-2xl flex flex-col flex-shrink-0 border border-white/5 shadow-2xl relative">
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none rounded-2xl"></div>
      
      <div className="h-20 flex items-center px-6 border-b border-white/10 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Plataforma<span className="text-primary-400">.</span>
          </h1>
        </div>
      </div>
      
      <nav className="flex-1 px-4 py-6 space-y-6 overflow-y-auto relative z-10 custom-scrollbar">
        
        <div>
          <NavLink to="/dashboard" className={navItemClass}>
            <Building2 className="w-4 h-4 mr-3" />
            Visão Geral (Dashboard)
          </NavLink>
        </div>
        
        <div>
          <p className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="w-2 h-[1px] bg-gray-500"></span> Motor Financeiro
          </p>
          <NavLink to="/receitas-despesas" className={navItemClass}>
            <Landmark className="w-4 h-4 mr-3" />
            DRE Gerencial (Fluxo)
          </NavLink>
          <NavLink to="/executions" className={navItemClass}>
            <CheckCheck className="w-4 h-4 mr-3" />
            Conciliação (Fuzzy)
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="w-2 h-[1px] bg-gray-500"></span> Motor Fiscal
          </p>
          <NavLink to="/documentos-fiscais" className={navItemClass}>
            <ReceiptText className="w-4 h-4 mr-3" />
            Apurações Mensais
          </NavLink>
          <NavLink to="/crm" className={navItemClass}>
            <BarChart3 className="w-4 h-4 mr-3" />
            Config. Regimes Tributários
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="w-2 h-[1px] bg-gray-500"></span> Motor Contábil
          </p>
          <NavLink to="/exportacao-contabil" className={navItemClass}>
            <FileSpreadsheet className="w-4 h-4 mr-3" />
            Geração SPED (Celery)
          </NavLink>
        </div>
      </nav>
      
      <div className="p-4 border-t border-white/10 relative z-10 flex flex-col gap-2">
        <NavLink to="/settings" className={navItemClass}>
          <Settings className="w-4 h-4 mr-3" />
          Configurações
        </NavLink>
        <NavLink to="/ui" className={navItemClass}>
          <Sparkles className="w-4 h-4 mr-3" />
          Design System UI
        </NavLink>
      </div>
    </aside>
  );
};
