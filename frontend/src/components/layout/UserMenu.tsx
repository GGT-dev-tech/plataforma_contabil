import React from 'react';
import { useAuth } from '../../auth/AuthProvider';
import { LogOut, User } from 'lucide-react';
import { Button } from '../ui/Button';

export const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="flex items-center gap-4">
      <div className="text-right hidden sm:block">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 leading-none mb-1">{user.nome}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 leading-none">{user.role}</p>
      </div>
      <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-300">
        <User className="w-5 h-5" />
      </div>
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={logout} 
        title="Sair"
        className="px-2"
        aria-label="Sair da aplicação"
      >
        <LogOut className="w-5 h-5 text-gray-500 hover:text-red-500 transition-colors" />
      </Button>
    </div>
  );
};
