import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthContextType } from './authTypes';
import { authService } from './authService';
import { User, Role } from '../types/user';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = authService.getToken();
      if (storedToken) {
        const payload = authService.parseJwt(storedToken);
        if (payload && payload.exp * 1000 > Date.now()) {
          // No MVP, vamos mockar o resgate do usuario baseado no token.
          // Numa app real, chamaríamos /api/v1/auth/me
          const loggedUser: User = {
            id: payload.sub,
            email: payload.email,
            nome: payload.nome,
            role: payload.role as Role
          };
          setToken(storedToken);
          setUser(loggedUser);
        } else {
          authService.clearToken();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = (newToken: string, userData: User) => {
    authService.setToken(newToken);
    setToken(newToken);
    setUser(userData);
  };

  const logout = () => {
    authService.clearToken();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
