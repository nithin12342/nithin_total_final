import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
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
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service functions
export const api = {
  // Authentication
  login: (credentials) => apiClient.post('/api/auth/login', credentials),
  register: (userData) => apiClient.post('/api/auth/register', userData),
  
  // Supply Chain APIs
  getInventory: (params) => apiClient.get('/api/supply/inventory', { params }),
  getInventoryById: (id) => apiClient.get(`/api/supply/inventory/${id}`),
  createInventory: (data) => apiClient.post('/api/supply/inventory', data),
  updateInventory: (id, data) => apiClient.put(`/api/supply/inventory/${id}`, data),
  deleteInventory: (id) => apiClient.delete(`/api/supply/inventory/${id}`),
  
  getShipments: (params) => apiClient.get('/api/supply/shipments', { params }),
  getShipmentById: (id) => apiClient.get(`/api/supply/shipments/${id}`),
  createShipment: (data) => apiClient.post('/api/supply/shipments', data),
  updateShipment: (id, data) => apiClient.put(`/api/supply/shipments/${id}`, data),
  deleteShipment: (id) => apiClient.delete(`/api/supply/shipments/${id}`),
  trackShipment: (id) => apiClient.get(`/api/supply/shipments/${id}/track`),
  
  getSuppliers: () => apiClient.get('/api/supply/suppliers'),
  getSupplierById: (id) => apiClient.get(`/api/supply/suppliers/${id}`),
  createSupplier: (data) => apiClient.post('/api/supply/suppliers', data),
  updateSupplier: (id, data) => apiClient.put(`/api/supply/suppliers/${id}`, data),
  deleteSupplier: (id) => apiClient.delete(`/api/supply/suppliers/${id}`),
  
  getOrders: (params) => apiClient.get('/api/supply/orders', { params }),
  getOrderById: (id) => apiClient.get(`/api/supply/orders/${id}`),
  createOrder: (data) => apiClient.post('/api/supply/orders', data),
  
  // Analytics APIs
  getInventoryAnalytics: () => apiClient.get('/api/supply/analytics/inventory'),
  getSupplyChainMetrics: () => apiClient.get('/api/supply/analytics/metrics'),
  getFinancialMetrics: () => apiClient.get('/api/supply/analytics/financial'),
  
  // AI/ML APIs
  getDemandForecast: (productId, period = 'WEEKLY') => 
    apiClient.get(`/api/supply/analytics/demand-forecast/${productId}`, { params: { period } }),
  getSupplierRiskAssessment: (supplierId) => 
    apiClient.get(`/api/supply/analytics/risk-assessment/supplier/${supplierId}`),
  
  // Finance APIs
  getInvoices: (params) => apiClient.get('/api/finance/invoices', { params }),
  getInvoiceById: (id) => apiClient.get(`/api/finance/invoices/${id}`),
  createInvoice: (data) => apiClient.post('/api/finance/invoices', data),
  updateInvoice: (id, data) => apiClient.put(`/api/finance/invoices/${id}`, data),
  deleteInvoice: (id) => apiClient.delete(`/api/finance/invoices/${id}`),
  
  getPayments: (params) => apiClient.get('/api/finance/payments', { params }),
  getPaymentById: (id) => apiClient.get(`/api/finance/payments/${id}`),
  createPayment: (data) => apiClient.post('/api/finance/payments', data),
  
  // Dashboard
  getDashboardMetrics: () => apiClient.get('/api/dashboard/metrics'),
  getDashboardTransactions: () => apiClient.get('/api/dashboard/transactions'),
  
  // AI Model Monitoring APIs
  getModelPerformanceMetrics: () => apiClient.get('/api/ai/monitoring/performance'),
  triggerModelRetraining: () => apiClient.post('/api/ai/monitoring/retrain'),
};

export default apiClient;