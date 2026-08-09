import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface Workspace {
  id: string;
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  import_config?: Record<string, any> | null;
}

interface WorkspaceContextType {
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  setActiveWorkspaceId: (id: string | null) => void;
  activeWorkspace: Workspace | null;
  isLoading: boolean;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceIdState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Carrega as empresas da API
  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/workspaces/empresas');
        if (response.ok) {
          const data = await response.json();
          setWorkspaces(data);
          
          // Tenta recuperar do localStorage, se não, pega o primeiro da lista
          const savedId = localStorage.getItem('activeWorkspaceId');
          if (savedId && data.find((w: Workspace) => w.id === savedId)) {
            setActiveWorkspaceIdState(savedId);
          } else if (data.length > 0) {
            setActiveWorkspaceIdState(data[0].id);
            localStorage.setItem('activeWorkspaceId', data[0].id);
          }
        }
      } catch (error) {
        console.error("Erro ao carregar workspaces:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWorkspaces();
  }, []);

  const setActiveWorkspaceId = (id: string | null) => {
    setActiveWorkspaceIdState(id);
    if (id) {
      localStorage.setItem('activeWorkspaceId', id);
    } else {
      localStorage.removeItem('activeWorkspaceId');
    }
  };

  const activeWorkspace = workspaces.find(w => w.id === activeWorkspaceId) || null;

  return (
    <WorkspaceContext.Provider value={{ workspaces, activeWorkspaceId, setActiveWorkspaceId, activeWorkspace, isLoading }}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}
