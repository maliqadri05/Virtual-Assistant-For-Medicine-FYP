/**
 * Advanced API Service Layer with Retry Logic & Interceptors
 * Handles all API calls with automatic retry, error handling, and request/response interception
 */

import * as authService from '@/services/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const MAX_RETRIES = 3;
const TIMEOUT = 30000; // 30 seconds

/**
 * Request configuration interface
 */
interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  retries?: number;
  shouldRetry?: (error: any, attempt: number) => boolean;
}

/**
 * Request/Response Interceptor Types
 */
type RequestInterceptor = (config: RequestInit) => RequestInit | Promise<RequestInit>;
type ResponseInterceptor = (response: Response) => Response | Promise<Response>;
type ErrorInterceptor = (error: Error) => Error | Promise<Error>;

/**
 * Interceptor Manager
 */
class InterceptorManager {
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];

  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  addErrorInterceptor(interceptor: ErrorInterceptor): void {
    this.errorInterceptors.push(interceptor);
  }

  async executeRequest(config: RequestInit): Promise<RequestInit> {
    let finalConfig = config;
    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig);
    }
    return finalConfig;
  }

  async executeResponse(response: Response): Promise<Response> {
    let finalResponse = response;
    for (const interceptor of this.responseInterceptors) {
      finalResponse = await interceptor(finalResponse);
    }
    return finalResponse;
  }

  async executeError(error: Error): Promise<Error> {
    let finalError = error;
    for (const interceptor of this.errorInterceptors) {
      finalError = await interceptor(finalError);
    }
    return finalError;
  }

  clear(): void {
    this.requestInterceptors = [];
    this.responseInterceptors = [];
    this.errorInterceptors = [];
  }
}

/**
 * Main API Service
 */
class ApiService {
  private baseUrl: string;
  private maxRetries: number;
  private timeout: number;
  private interceptors = new InterceptorManager();

  constructor(baseUrl: string = API_URL, maxRetries: number = MAX_RETRIES) {
    this.baseUrl = baseUrl;
    this.maxRetries = maxRetries;
    this.timeout = TIMEOUT;
    this.setupDefaultInterceptors();
  }

  /**
   * Setup default interceptors
   */
  private setupDefaultInterceptors(): void {
    // Add auth headers
    this.interceptors.addRequestInterceptor(async (config) => {
      const headers = (config.headers as Record<string, string>) || {};
      
      // Use new auth service method
      const token = authService.getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      return {
        ...config,
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
      };
    });

    // Handle 401 responses with token refresh
    this.interceptors.addResponseInterceptor(async (response) => {
      if (response.status === 401) {
        try {
          await authService.refreshAccessToken();
          // Caller should retry the request
        } catch (error) {
          await authService.logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
      }
      return response;
    });

    // Log errors
    this.interceptors.addErrorInterceptor((error) => {
      console.error('API Error:', error);
      return error;
    });
  }

  /**
   * Get interceptor manager for custom interceptors
   */
  getInterceptors() {
    return this.interceptors;
  }

  /**
   * Delay helper for backoff
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Make fetchwith retry logic
   */
  private async fetchWithRetry(
    url: string,
    config: RequestInit,
    options: RequestOptions
  ): Promise<Response> {
    let lastError: Error | null = null;
    const maxAttempts = options.retries ?? this.maxRetries;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(
          () => controller.abort(),
          options.timeout ?? this.timeout
        );

        const response = await fetch(url, {
          ...config,
          signal: controller.signal,
        });

        clearTimeout(timeout);

        // Don't retry on client errors (except 401)
        if (response.status < 500 && response.status !== 408 && response.status !== 401) {
          return response;
        }

        // Retry on server errors
        if (attempt < maxAttempts - 1) {
          await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
          continue;
        }

        return response;
      } catch (error: any) {
        lastError = error;

        const shouldRetry = options.shouldRetry
          ? options.shouldRetry(error, attempt)
          : error.name === 'AbortError' || error instanceof TypeError;

        if (shouldRetry && attempt < maxAttempts - 1) {
          await this.delay(Math.pow(2, attempt) * 1000);
          continue;
        }

        throw error;
      }
    }

    throw lastError || new Error('Max retries exceeded');
  }

  /**
   * Make authenticated API request
   */
  async apiCall(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<Response> {
    const {
      method = 'GET',
      headers = {},
      body,
    } = options;

    const url = `${this.baseUrl}${endpoint}`;

    let config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (body && method !== 'GET') {
      config.body = typeof body === 'string' ? body : JSON.stringify(body);
    }

    // Execute request interceptors
    config = await this.interceptors.executeRequest(config);

    try {
      const response = await this.fetchWithRetry(url, config, options);

      // Execute response interceptors
      const processedResponse = await this.interceptors.executeResponse(response);

      if (!processedResponse.ok && processedResponse.status !== 401) {
        const errorData = await processedResponse.json().catch(() => ({}));
        const error = new Error(
          errorData.message || errorData.detail || `HTTP Error: ${processedResponse.status}`
        );
        (error as any).status = processedResponse.status;
        (error as any).data = errorData;
        throw error;
      }

      return processedResponse;
    } catch (error: any) {
      // Execute error interceptors
      await this.interceptors.executeError(error);
      throw error;
    }
  }

  /**
   * Generic request method
   */
  async request<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const response = await this.apiCall(endpoint, options);
    
    if (response.status === 204) {
      return {} as T; // No content
    }

    const data = await response.json();
    return data;
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  /**
   * Set base URL
   */
  setBaseUrl(url: string): void {
    this.baseUrl = url;
  }

  /**
   * Get base URL
   */
  getBaseUrl(): string {
    return this.baseUrl;
  }
}

// Create and export singleton instance
const apiService = new ApiService();

// Convenience exports
export { ApiService };
export type { RequestOptions };
export default apiService;

/**
 * HTTP Methods (aliased for backward compatibility)
 */
export const get = <T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
  apiService.get<T>(endpoint, options);

export const post = <T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>) =>
  apiService.post<T>(endpoint, body, options);

export const put = <T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>) =>
  apiService.put<T>(endpoint, body, options);

export const patch = <T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>) =>
  apiService.patch<T>(endpoint, body, options);

export const del = <T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
  apiService.delete<T>(endpoint, options);

/**
 * Conversation API Endpoints
 */
export const conversationAPI = {
  /**
   * Create new conversation
   */
  create: (data?: { patient_context?: Record<string, unknown> }) =>
    apiService.post('/conversations', data || {}),

  /**
   * Get specific conversation
   */
  get: (id: string) =>
    apiService.get(`/conversations/${id}`),

  /**
   * List all conversations with pagination
   */
  list: (params?: { skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', String(params.skip));
    if (params?.limit) searchParams.append('limit', String(params.limit));
    const query = searchParams.toString();
    return apiService.get(`/conversations${query ? '?' + query : ''}`);
  },

  /**
   * Add message to conversation
   */
  addMessage: (id: string, message: string) =>
    apiService.post(`/conversations/${id}/messages`, { content: message }),

  /**
   * Get conversation report
   */
  getReport: (id: string) =>
    apiService.get<{ report: string }>(`/conversations/${id}/report`),

  /**
   * Export conversation as PDF
   */
  exportPDF: async (id: string) => {
    const response = await apiService.apiCall(`/conversations/${id}/export/pdf`);
    return response.blob();
  },

  /**
   * Share conversation
   */
  share: (id: string, email: string) =>
    apiService.post(`/conversations/${id}/share`, { email }),

  /**
   * Delete conversation
   */
  delete: (id: string) =>
    apiService.delete(`/conversations/${id}`),

  /**
   * Search conversations
   */
  search: (query: string) =>
    apiService.get(`/conversations/search?q=${encodeURIComponent(query)}`),

  /**
   * Get conversation stats
   */
  getStats: () =>
    apiService.get('/conversations/stats'),
};

/**
 * Patient API Endpoints
 */
export const patientAPI = {
  /**
   * Get patient profile
   */
  getProfile: () =>
    apiService.get('/patient/profile'),

  /**
   * Update patient profile
   */
  updateProfile: (data: Record<string, unknown>) =>
    apiService.put('/patient/profile', data),

  /**
   * Get medical history
   */
  getMedicalHistory: () =>
    apiService.get('/patient/medical-history'),

  /**
   * Update medical history
   */
  updateMedicalHistory: (data: Record<string, unknown>) =>
    apiService.put('/patient/medical-history', data),

  /**
   * Get allergies
   */
  getAllergies: () =>
    apiService.get('/patient/allergies'),

  /**
   * Add allergy
   */
  addAllergy: (allergy: string) =>
    apiService.post('/patient/allergies', { allergy }),

  /**
   * Get medications
   */
  getMedications: () =>
    apiService.get('/patient/medications'),

  /**
   * Add medication
   */
  addMedication: (data: Record<string, unknown>) =>
    apiService.post('/patient/medications', data),
};

/**
 * Report API Endpoints
 */
export const reportAPI = {
  /**
   * Get report by ID
   */
  get: (id: string) =>
    apiService.get(`/reports/${id}`),

  /**
   * List all reports
   */
  list: (params?: { skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', String(params.skip));
    if (params?.limit) searchParams.append('limit', String(params.limit));
    const query = searchParams.toString();
    return apiService.get(`/reports${query ? '?' + query : ''}`);
  },

  /**
   * Export report as PDF
   */
  exportPDF: async (id: string) => {
    const response = await apiService.apiCall(`/reports/${id}/export/pdf`);
    return response.blob();
  },

  /**
   * Share report
   */
  share: (id: string, email: string) =>
    apiService.post(`/reports/${id}/share`, { email }),

  /**
   * Delete report
   */
  delete: (id: string) =>
    apiService.delete(`/reports/${id}`),
};
