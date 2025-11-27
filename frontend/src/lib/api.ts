import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const authApi = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Workflow endpoints
export const workflowApi = {
  list: () => api.get('/workflows'),
  get: (id: number) => api.get(`/workflows/${id}`),
  create: (data: any) => api.post('/workflows', data),
  update: (id: number, data: any) => api.put(`/workflows/${id}`, data),
  delete: (id: number) => api.delete(`/workflows/${id}`),
  execute: (id: number, data?: any) => api.post(`/workflows/${id}/execute`, data || {}),
  listExecutions: (id: number) => api.get(`/workflows/${id}/executions`),
};

// Execution endpoints
export const executionApi = {
  get: (id: number) => api.get(`/executions/${id}`),
  getLogs: (id: number) => api.get(`/executions/${id}/logs`),
};

// API Key endpoints
export const apiKeyApi = {
  list: () => api.get('/api-keys'),
  create: (data: { name: string; expires_at?: string }) => api.post('/api-keys', data),
  delete: (id: number) => api.delete(`/api-keys/${id}`),
  deactivate: (id: number) => api.patch(`/api-keys/${id}/deactivate`),
};
