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
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('@App:token');
    const storedUser = localStorage.getItem('@App:user');

    if (storedToken && storedUser && storedUser !== 'undefined') {
      try {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      } catch (e) {
        console.error("Erro ao fazer parse do usuário do localStorage", e);
        localStorage.removeItem('@App:user');
        localStorage.removeItem('@App:token');
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
