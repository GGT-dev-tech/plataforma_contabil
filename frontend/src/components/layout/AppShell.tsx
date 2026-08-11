import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Outlet } from 'react-router-dom';

export const AppShell: React.FC = () => {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden text-slate-900 font-sans relative">
      <div className="flex w-full h-full p-0 sm:p-2 md:p-4 gap-4">
        {/* Sidebar fixa e nítida */}
        <div className="hidden md:block w-64 flex-shrink-0 z-20">
          <Sidebar />
        </div>
        
        {/* Área Principal Branca e Sólida */}
        <div className="flex-1 flex flex-col min-w-0 bg-white rounded-none sm:rounded-xl overflow-hidden shadow-sm border border-slate-200 relative z-10">
          <Header />
          <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-8 scroll-smooth bg-slate-50/50">
            <div className="max-w-7xl mx-auto w-full animate-fade-in">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
