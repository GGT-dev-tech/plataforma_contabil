import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, User, Settings } from 'lucide-react';
import { 
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from '../ui/DropdownMenu';

export const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-3 outline-none rounded-full focus-visible:ring-2 focus-visible:ring-blue-500 ring-offset-background p-1 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
        <div className="text-right hidden sm:block px-2">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 leading-none mb-1">{user.nome}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 leading-none">{user.role}</p>
        </div>
        <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-300">
          <User className="w-5 h-5" />
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Minha Conta</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Settings className="mr-2 h-4 w-4" />
          <span>Configurações</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-700 dark:text-red-400 dark:focus:text-red-300 focus:bg-red-50 dark:focus:bg-red-900/20">
          <LogOut className="mr-2 h-4 w-4" />
          <span>Sair</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
