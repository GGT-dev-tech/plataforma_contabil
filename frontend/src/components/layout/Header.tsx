import React from 'react';
import { UserMenu } from './UserMenu';
import { WorkspaceSelector } from '../WorkspaceSelector';

export const Header: React.FC = () => {
  return (
    <header className="h-16 glass border-b border-l flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex-1">
        <WorkspaceSelector />
      </div>
      <UserMenu />
    </header>
  );
};
