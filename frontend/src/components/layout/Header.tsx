import React from 'react';
import { UserMenu } from './UserMenu';
import { WorkspaceSelector } from '../WorkspaceSelector';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-white/80 border-b border-slate-200 flex items-center justify-between px-6 sm:px-8 sticky top-0 z-20 backdrop-blur-md">
      <div className="flex-1 flex items-center gap-4">
        <WorkspaceSelector />
      </div>
      <div className="flex items-center gap-4">
        <UserMenu />
      </div>
    </header>
  );
};
