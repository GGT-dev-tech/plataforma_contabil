import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './queryClient';
import { AuthProvider } from '../auth/AuthProvider';
import { WorkspaceProvider } from '../contexts/WorkspaceContext';
// import { ThemeProvider } from '../theme/ThemeProvider'; // To be implemented
// import { ModalProvider } from '../components/ui/ModalProvider'; // To be implemented
// import { NotificationProvider } from '../components/ui/NotificationProvider'; // To be implemented

export const Providers: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WorkspaceProvider>
        {/* <ThemeProvider> */}
          {/* <NotificationProvider> */}
            {/* <ModalProvider> */}
              {children}
            {/* </ModalProvider> */}
          {/* </NotificationProvider> */}
        {/* </ThemeProvider> */}
        </WorkspaceProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};
