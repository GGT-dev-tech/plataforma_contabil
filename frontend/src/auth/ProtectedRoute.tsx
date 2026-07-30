import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { hasPermission } from './permissions';
import { Role } from '../types/user';

interface ProtectedRouteProps {
  allowedRoles?: Role[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <div>Carregando sessão...</div>; // TODO: Melhorar UI de loading global
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !hasPermission(user.role, allowedRoles)) {
    // Se logado mas sem permissão pra rota específica
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};
