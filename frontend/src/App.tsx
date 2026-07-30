import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthProvider';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { Login } from './pages/Login';
import { NewExecution } from './pages/NewExecution';
import { CandidatesQueue } from './pages/CandidatesQueue';
import { Divergencies } from './pages/Divergencies';
import { NavBar } from './components/NavBar';
import { PERMISSIONS } from './auth/permissions';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div>
      <NavBar />
      <main style={{ padding: '2rem' }}>
        {children}
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            {/* Rotas protegidas gerais */}
            <Route path="/" element={<Navigate to="/candidates" replace />} />
            <Route path="/unauthorized" element={<div>Acesso Negado</div>} />
            
            {/* Rotas de Leitura/Revisão (Auditores também veem) */}
            <Route element={<ProtectedRoute allowedRoles={PERMISSIONS.CAN_VIEW_DASHBOARD} />}>
              <Route path="/candidates" element={<Layout><CandidatesQueue /></Layout>} />
              <Route path="/divergencies" element={<Layout><Divergencies /></Layout>} />
            </Route>
            
            {/* Rotas específicas de operacionais (Apenas Analistas/Admins) */}
            <Route element={<ProtectedRoute allowedRoles={PERMISSIONS.CAN_CREATE_EXECUTION} />}>
              <Route path="/executions/new" element={<Layout><NewExecution /></Layout>} />
            </Route>
            
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
