import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Outlet } from 'react-router-dom';

export const AppShell: React.FC = () => {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-[#0b0f19] overflow-hidden text-gray-900 dark:text-gray-100 font-sans relative">
      {/* Dynamic Animated Blobs for Glassmorphism Background */}
      <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob -z-10 pointer-events-none"></div>
      <div className="fixed top-[20%] right-[-10%] w-[35%] h-[35%] bg-accent-500/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000 -z-10 pointer-events-none"></div>
      <div className="fixed bottom-[-15%] left-[20%] w-[50%] h-[40%] bg-blue-500/10 rounded-full mix-blend-screen filter blur-[120px] animate-blob animation-delay-4000 -z-10 pointer-events-none"></div>

      <div className="flex w-full h-full p-2 md:p-4 gap-4">
        {/* Floating Sidebar */}
        <div className="hidden md:block w-64 flex-shrink-0 z-20">
          <Sidebar />
        </div>
        
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 rounded-2xl glass overflow-hidden shadow-2xl relative z-10 border border-white/10">
          <Header />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-transparent p-4 md:p-8 scroll-smooth">
            <div className="max-w-7xl mx-auto w-full animate-fade-in">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
