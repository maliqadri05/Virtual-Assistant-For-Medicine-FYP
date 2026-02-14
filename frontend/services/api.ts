// API service for backend integration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
}

/**
 * Make authenticated API request
 */
export async function apiCall(
  endpoint: string,
  options: RequestOptions = {}
): Promise<Response> {
  const {
    method = 'GET',
    headers = {},
    body,
    timeout = 30000,
  } = options;

  const url = `${API_URL}${endpoint}`;

  // Add authorization header if token exists
  const token = getAuthToken();
  const finalHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (token) {
    finalHeaders['Authorization'] = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      method,
      headers: finalHeaders,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 401) {
        clearAuthToken();
        window.location.href = '/login';
      }
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

/**
 * GET request
 */
export async function get<T>(endpoint: string): Promise<T> {
  const response = await apiCall(endpoint, { method: 'GET' });
  return response.json();
}

/**
 * POST request
 */
export async function post<T>(endpoint: string, data: unknown): Promise<T> {
  const response = await apiCall(endpoint, { method: 'POST', body: data });
  return response.json();
}

/**
 * PUT request
 */
export async function put<T>(endpoint: string, data: unknown): Promise<T> {
  const response = await apiCall(endpoint, { method: 'PUT', body: data });
  return response.json();
}

/**
 * DELETE request
 */
export async function del<T>(endpoint: string): Promise<T> {
  const response = await apiCall(endpoint, { method: 'DELETE' });
  return response.json();
}

/**
 * Get auth token from storage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Clear auth token
 */
function clearAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
}

/**
 * Conversation API endpoints
 */
export const conversationAPI = {
  create: (data: { patient_context?: Record<string, unknown> }) =>
    post('/api/conversations', data),

  get: (id: string) =>
    get(`/api/conversations/${id}`),

  list: () =>
    get('/api/conversations'),

  addMessage: (id: string, message: string) =>
    post(`/api/conversations/${id}/messages`, { content: message }),

  getReport: (id: string) =>
    get<{ report: string }>(`/api/conversations/${id}/report`),

  exportPDF: (id: string) =>
    apiCall(`/api/conversations/${id}/export/pdf`),
};

/**
 * Authentication API endpoints
 */
export const authAPI = {
  login: (email: string, password: string) =>
    post<{ token: string }>('/api/auth/login', { email, password }),

  logout: () => {
    clearAuthToken();
    return Promise.resolve();
  },

  register: (email: string, password: string, name: string) =>
    post('/api/auth/register', { email, password, name }),

  refreshToken: () =>
    post<{ token: string }>('/api/auth/refresh', {}),
};

/**
 * Patient API endpoints
 */
export const patientAPI = {
  getProfile: () =>
    get('/api/patient/profile'),

  updateProfile: (data: Record<string, unknown>) =>
    put('/api/patient/profile', data),

  getMedicalHistory: () =>
    get('/api/patient/medical-history'),

  updateMedicalHistory: (data: Record<string, unknown>) =>
    put('/api/patient/medical-history', data),
};
