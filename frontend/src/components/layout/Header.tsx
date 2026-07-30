import React from 'react';
import { UserMenu } from './UserMenu';

export const Header: React.FC = () => {
  return (
    <header className="h-16 glass border-b border-l flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex-1">
        {/* Placeholder for future global search or breadcrumbs if moved here */}
      </div>
      <UserMenu />
    </header>
  );
};
