import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Settings } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 flex-shrink-0 glass border-r flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-gray-200/50 dark:border-gray-700/50">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
          Plataforma
        </h1>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        <NavLink 
          to="/executions"
          className={({ isActive }) => `
            flex items-center px-4 py-2.5 rounded-lg transition-colors duration-200 group font-medium text-sm
            ${isActive 
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'}
          `}
        >
          <LayoutDashboard className="w-5 h-5 mr-3" />
          Execuções
        </NavLink>
        <NavLink 
          to="/ui"
          className={({ isActive }) => `
            flex items-center px-4 py-2.5 rounded-lg transition-colors duration-200 group font-medium text-sm
            ${isActive 
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'}
          `}
        >
          <Settings className="w-5 h-5 mr-3" />
          Showcase UI
        </NavLink>
      </nav>
    </aside>
  );
};
