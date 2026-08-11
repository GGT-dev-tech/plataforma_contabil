import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

export const NavBar: React.FC = () => {
  const { user, logout } = useAuth();
  
  return (
    <nav style={{ padding: '1rem', backgroundColor: '#1f2937', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 'bold' }}>Plataforma Contábil</h1>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/executions" style={{ color: '#d1d5db', textDecoration: 'none' }}>Execuções</Link>
          {user && (user.role === 'ADMIN' || user.role === 'ANALISTA') && (
            <Link to="/executions/new" style={{ color: '#d1d5db', textDecoration: 'none' }}>Nova Execução</Link>
          )}
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>{user?.nome} ({user?.role})</span>
        <button 
          onClick={logout}
          style={{ padding: '0.5rem 1rem', backgroundColor: 'transparent', color: '#f87171', border: '1px solid #f87171', borderRadius: '4px', cursor: 'pointer' }}
        >
          Sair
        </button>
      </div>
    </nav>
  );
};
