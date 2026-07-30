import React from 'react';
import { Providers } from './app/providers';
import { AppRouter } from './app/router';

export const App: React.FC = () => {
  return (
    <Providers>
      <AppRouter />
    </Providers>
  );
};

export default App;
