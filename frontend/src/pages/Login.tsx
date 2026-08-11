import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../auth/authService';
import { useNavigate } from 'react-router-dom';
import { User, Role } from '../types/user';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const getLoginUrl = () => {
    // 1. Runtime config injected by docker-entrypoint.sh (most reliable in Railway)
    const runtimeUrl = (window as any).__API_URL__;
    // 2. Build-time VITE env var
    const buildTimeUrl = import.meta.env.VITE_API_URL;
    
    let envUrl = ((runtimeUrl || buildTimeUrl || '') as string).trim();
    
    if (!envUrl) {
      return '/api/v1/auth/login';
    }
    
    envUrl = envUrl.replace(/\/+$/, '');
    // Strip /auth or /auth/login suffix if user accidentally included it
    envUrl = envUrl.replace(/\/auth\/login$/, '').replace(/\/auth$/, '');
    
    if (!envUrl.endsWith('/api/v1')) {
      envUrl = `${envUrl}/api/v1`;
    }
    
    return `${envUrl}/auth/login`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const targetUrl = getLoginUrl();
      console.log("Enviando login para URL:", targetUrl);

      const response = await fetch(targetUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      if (response.status === 405) {
        throw new Error('ERR_405_STATIC_SERVER');
      }

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Credenciais inválidas. Verifique e-mail e senha.');
        }
        throw new Error(`Erro na API (${response.status})`);
      }
      
      const data = await response.json();
      const payload = authService.parseJwt(data.access_token);
      
      const user: User = {
        id: payload.sub,
        email: payload.email,
        nome: payload.nome,
        role: payload.role as Role
      };
      
      login(data.access_token, user);
      navigate('/');
    } catch (err: any) {
      console.error("Erro de Login capturado:", err);
      let errorMsg = err.message || 'Erro ao realizar login';
      
      if (errorMsg === 'ERR_405_STATIC_SERVER') {
        errorMsg = 'Erro 405: A requisição de login está caindo no servidor do Frontend em vez do Backend. Configure VITE_API_URL no Railway do Frontend apontando para o seu Backend (ex: https://seu-backend.up.railway.app).';
      } else if (err instanceof SyntaxError || errorMsg.includes('Unexpected token')) {
        errorMsg = 'Erro de conexão com a API. Verifique se a variável VITE_API_URL no Frontend está apontando para a URL correta do Backend no Railway.';
      } else if (errorMsg === 'Failed to fetch') {
        errorMsg = 'Falha de rede (CORS ou Backend fora do ar). Verifique as variáveis VITE_API_URL no Frontend e CORS_ORIGINS no Backend.';
      }
      
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f3f4f6' }}>
      <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', width: '100%', maxWidth: '400px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', textAlign: 'center' }}>Plataforma Contábil</h1>
        
        {error && (
          <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500' }}>Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '4px' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500' }}>Senha</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '4px' }}
            />
          </div>
          
          <button 
            type="submit" 
            disabled={isLoading}
            style={{ 
              marginTop: '0.5rem', 
              padding: '0.75rem', 
              backgroundColor: isLoading ? '#9ca3af' : '#2563eb', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  );
};
