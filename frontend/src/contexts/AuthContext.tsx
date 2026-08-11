import React, { createContext, useContext, useState, useEffect } from 'react';

import { User } from '../types/user';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('@App:token'));
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem('@App:user');
    if (storedUser && storedUser !== 'undefined') {
      try {
        return JSON.parse(storedUser);
      } catch (e) {
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    // Apenas garante limpeza em caso de erro, já foi lido no useState
    const storedToken = localStorage.getItem('@App:token');
    const storedUser = localStorage.getItem('@App:user');

    if (storedToken && storedUser && storedUser !== 'undefined') {
      try {
        JSON.parse(storedUser); // Valida
      } catch (e) {
        console.error("Erro ao fazer parse do usuário do localStorage", e);
        localStorage.removeItem('@App:user');
        localStorage.removeItem('@App:token');
        setToken(null);
        setUser(null);
      }
    }
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('@App:token', newToken);
    localStorage.setItem('@App:user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('@App:token');
    localStorage.removeItem('@App:user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};
