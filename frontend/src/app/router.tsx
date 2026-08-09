import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../auth/ProtectedRoute';

import { LoginPage } from '../pages/auth/LoginPage';
import { NewExecution } from '../pages/NewExecution';
import { ExecutionsList } from '../pages/ExecutionsList';
import { ExecutionView } from '../pages/ExecutionView';
import { Showcase } from '../pages/Showcase';
import { AppShell } from '../components/layout/AppShell';

import { StagingGrid } from '../pages/StagingGrid';
import { WorkspaceSettings } from '../pages/WorkspaceSettings';
import { DashboardClientes } from '../pages/DashboardClientes';
import { ObrasPage } from '../pages/obras/ObrasPage';
import { DocumentosFiscaisPage } from '../pages/fiscal/DocumentosFiscaisPage';
import { DashboardTributario } from '../pages/dashboard/DashboardTributario';
import { ExportacaoContabilPage } from '../pages/exportacao/ExportacaoContabilPage';

export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardClientes />} />
          <Route path="/unauthorized" element={<div className="p-12 text-center text-xl">Acesso Negado</div>} />
          
          <Route element={<AppShell />}>
            <Route path="/ui" element={<Showcase />} />
            
            <Route element={<ProtectedRoute />}>
              <Route path="/executions" element={<ExecutionsList />} />
              <Route path="/executions/:id" element={<ExecutionView />} />
              <Route path="/executions/:id/staging" element={<StagingGrid />} />
            </Route>
            
            <Route element={<ProtectedRoute />}>
              <Route path="/executions/new" element={<NewExecution />} />
              <Route path="/settings" element={<WorkspaceSettings />} />
              <Route path="/dashboard" element={<DashboardTributario />} />
              <Route path="/obras" element={<ObrasPage />} />
              <Route path="/documentos-fiscais" element={<DocumentosFiscaisPage />} />
              <Route path="/exportacao-contabil" element={<ExportacaoContabilPage />} />
            </Route>
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
