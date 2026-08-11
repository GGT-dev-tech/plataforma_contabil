// Build: 2026-08-09T20:50:00Z - force redeploy for VITE_API_URL
import axios from 'axios';

// Resolve API base URL - supports both build-time (VITE_API_URL) and runtime (window.__API_URL__)
const getBaseUrl = (): string => {
  // 1. Runtime config injected by docker-entrypoint.sh (most reliable in Railway)
  const runtimeUrl = (window as any).__API_URL__;
  // 2. Build-time config from Vite (VITE_API_URL in Railway env vars)
  const buildTimeUrl = import.meta.env.VITE_API_URL;
  
  let url = ((runtimeUrl || buildTimeUrl || '') as string).trim();
  
  // Fallback to relative path (works when frontend and backend are on same domain)
  if (!url) {
    return '/api/v1';
  }
  
  // Normalize: remove trailing slashes
  url = url.replace(/\/+$/, '');
  
  // Ensure /api/v1 suffix
  if (!url.endsWith('/api/v1') && !url.endsWith('/v1')) {
    url = `${url}/api/v1`;
  }
  
  return url;
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Injeta o Workspace Ativo (Tenant) em todas as chamadas API
    const activeWorkspaceId = localStorage.getItem('activeWorkspaceId');
    if (activeWorkspaceId) {
      config.headers['X-Tenant-ID'] = activeWorkspaceId;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
