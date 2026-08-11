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
      <DropdownMenuTrigger className="flex items-center gap-3 outline-none rounded-full focus-visible:ring-2 focus-visible:ring-primary-500 ring-offset-background p-1 hover:bg-slate-100 transition-colors">
        <div className="text-right hidden sm:block px-2">
          <p className="text-sm font-medium text-slate-900 leading-none mb-1">{user.nome}</p>
          <p className="text-xs text-slate-500 leading-none">{user.role}</p>
        </div>
        <div className="w-9 h-9 rounded-full bg-primary-50 flex items-center justify-center text-primary-600 border border-primary-100">
          <User className="w-5 h-5" />
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 bg-white border border-slate-200">
        <DropdownMenuLabel className="text-slate-700">Minha Conta</DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-slate-100" />
        <DropdownMenuItem className="text-slate-600 focus:bg-slate-50 focus:text-slate-900 cursor-pointer">
          <Settings className="mr-2 h-4 w-4" />
          <span>Configurações</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator className="bg-slate-100" />
        <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-700 focus:bg-red-50 cursor-pointer">
          <LogOut className="mr-2 h-4 w-4" />
          <span>Sair</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
