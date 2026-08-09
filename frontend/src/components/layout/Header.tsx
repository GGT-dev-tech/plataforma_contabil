import React from 'react';
import { UserMenu } from './UserMenu';
import { WorkspaceSelector } from '../WorkspaceSelector';

export const Header: React.FC = () => {
  return (
    <header className="h-20 bg-transparent border-b border-white/10 flex items-center justify-between px-8 sticky top-0 z-10 backdrop-blur-md">
      <div className="flex-1 flex items-center gap-4">
        <WorkspaceSelector />
      </div>
      <div className="flex items-center gap-4">
        <UserMenu />
      </div>
    </header>
  );
};
