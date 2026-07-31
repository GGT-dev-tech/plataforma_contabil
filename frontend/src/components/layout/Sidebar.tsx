import React from 'react';
import { NavLink } from 'react-router-dom';
import { Settings, Users, Receipt, Landmark, FileSpreadsheet, CheckCheck } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItemClass = ({ isActive }: { isActive: boolean }) => `
    flex items-center px-4 py-2 rounded-lg transition-colors duration-200 group font-medium text-sm
    ${isActive 
      ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' 
      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'}
  `;

  return (
    <aside className="w-64 flex-shrink-0 glass border-r flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-gray-200/50 dark:border-gray-700/50">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
          Plataforma Contábil
        </h1>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-4 overflow-y-auto">
        <div>
          <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Conciliações & Staging</p>
          <NavLink to="/executions" className={navItemClass}>
            <CheckCheck className="w-4 h-4 mr-3" />
            Execuções & Conciliação
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">CRM & Clientes</p>
          <NavLink to="/executions" className={navItemClass}>
            <Users className="w-4 h-4 mr-3" />
            Clientes & Propostas
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">ERP Financial</p>
          <NavLink to="/executions" className={navItemClass}>
            <Receipt className="w-4 h-4 mr-3" />
            Receitas & Despesas
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Bancos & Caixa</p>
          <NavLink to="/executions" className={navItemClass}>
            <Landmark className="w-4 h-4 mr-3" />
            Contas & Dinheiro
          </NavLink>
        </div>

        <div>
          <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Contábil & Fiscal</p>
          <NavLink to="/executions" className={navItemClass}>
            <FileSpreadsheet className="w-4 h-4 mr-3" />
            Razão & Apuração Fiscal
          </NavLink>
        </div>

        <div className="pt-4 border-t border-gray-200 dark:border-gray-700/50">
          <NavLink to="/ui" className={navItemClass}>
            <Settings className="w-4 h-4 mr-3" />
            Design System UI
          </NavLink>
        </div>
      </nav>
    </aside>
  );
};
