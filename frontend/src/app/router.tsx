import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { PERMISSIONS } from '../auth/permissions';

import { Login } from '../pages/Login';
import { NewExecution } from '../pages/NewExecution';
import { ExecutionsList } from '../pages/ExecutionsList';
import { ExecutionView } from '../pages/ExecutionView';
import { Showcase } from '../pages/Showcase';
import { AppShell } from '../components/layout/AppShell';

import { StagingGrid } from '../pages/StagingGrid';

export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Navigate to="/executions" replace />} />
          <Route path="/unauthorized" element={<div className="p-12 text-center text-xl">Acesso Negado</div>} />
          
          <Route element={<AppShell />}>
            <Route path="/ui" element={<Showcase />} />
            
            <Route element={<ProtectedRoute allowedRoles={PERMISSIONS.CAN_VIEW_DASHBOARD} />}>
              <Route path="/executions" element={<ExecutionsList />} />
              <Route path="/executions/:id" element={<ExecutionView />} />
              <Route path="/executions/:id/staging" element={<StagingGrid />} />
            </Route>
            
            <Route element={<ProtectedRoute allowedRoles={PERMISSIONS.CAN_CREATE_EXECUTION} />}>
              <Route path="/executions/new" element={<NewExecution />} />
            </Route>
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
