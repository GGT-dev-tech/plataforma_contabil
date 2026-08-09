import axios from 'axios';

const getBaseUrl = () => {
  let url = (import.meta.env.VITE_API_URL || '/api/v1').trim();
  url = url.replace(/\/+$/, '');
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
