import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  verify: () => api.get('/auth/verify'),
  refresh: () => api.post('/auth/refresh'),
  getProfile: () => api.get('/auth/profile'),
};

// Simulations API
export const simulationsAPI = {
  getAll: (params = {}) => api.get('/simulations', { params }),
  getById: (id) => api.get(`/simulations/${id}`),
  create: (data) => api.post('/simulations', data),
  start: (id) => api.post(`/simulations/${id}/start`),
  stop: (id) => api.post(`/simulations/${id}/stop`),
  pause: (id) => api.post(`/simulations/${id}/pause`),
  resume: (id) => api.post(`/simulations/${id}/resume`),
  delete: (id) => api.delete(`/simulations/${id}`),
  getProgress: (id) => api.get(`/simulations/${id}/progress`),
  getTemplates: () => api.get('/simulations/templates'),
  getStats: () => api.get('/simulations/stats'),
};

// Metrics API
export const metricsAPI = {
  getOverview: (period = '24h') => api.get('/metrics/overview', { params: { period } }),
  getTimeSeries: (type, period = '1h', resolution = 'minute') => 
    api.get('/metrics/timeseries', { params: { type, period, resolution } }),
  getEndpoints: () => api.get('/metrics/endpoints'),
  getStatusCodes: () => api.get('/metrics/status-codes'),
  getErrors: () => api.get('/metrics/errors'),
  getPerformance: () => api.get('/metrics/performance'),
  getRealtime: () => api.get('/metrics/realtime'),
  exportMetrics: (data) => api.post('/metrics/export', data),
};

// Configurations API
export const configurationsAPI = {
  getTemplates: (params = {}) => api.get('/configurations/templates', { params }),
  getTemplate: (id) => api.get(`/configurations/templates/${id}`),
  createTemplate: (data) => api.post('/configurations/templates', data),
  updateTemplate: (id, data) => api.put(`/configurations/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/configurations/templates/${id}`),
  validateConfig: (data) => api.post('/configurations/validate', data),
  testConnection: (data) => api.post('/configurations/test-connection', data),
  getSaved: () => api.get('/configurations/saved'),
  saveConfig: (data) => api.post('/configurations/saved', data),
  deleteSaved: (id) => api.delete(`/configurations/saved/${id}`),
};

// System API
export const systemAPI = {
  getHealth: () => api.get('/health'),
  getSystemInfo: () => api.get('/system/info'),
};

export default api;