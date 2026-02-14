// Authentication service with JWT token handling
import { setStorageItem, getStorageItem, removeStorageItem } from '@/services/storage';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  name?: string;
  avatar?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  user: User;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!getStorageItem(ACCESS_TOKEN_KEY);
}

/**
 * Get current user
 */
export function getCurrentUser(): User | null {
  const userStr = getStorageItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Get access token
 */
export function getAccessToken(): string | null {
  return getStorageItem(ACCESS_TOKEN_KEY);
}

/**
 * Get refresh token
 */
export function getRefreshToken(): string | null {
  return getStorageItem(REFRESH_TOKEN_KEY);
}

/**
 * Save auth tokens and user
 */
export function setAuth(data: AuthResponse): void {
  setStorageItem(ACCESS_TOKEN_KEY, data.access_token);
  if (data.refresh_token) {
    setStorageItem(REFRESH_TOKEN_KEY, data.refresh_token);
  }
  setStorageItem(USER_KEY, JSON.stringify(data.user));
}

/**
 * Clear authentication
 */
export function clearAuth(): void {
  removeStorageItem(ACCESS_TOKEN_KEY);
  removeStorageItem(REFRESH_TOKEN_KEY);
  removeStorageItem(USER_KEY);
}

/**
 * Get authorization header
 */
export function getAuthHeader(): Record<string, string> {
  const token = getAccessToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

/**
 * Login user with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  try {
    const response = await fetch(`${apiUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    setAuth(data);
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Register new user
 */
export async function register(
  firstName: string,
  lastName: string,
  email: string,
  password: string
): Promise<AuthResponse> {
  try {
    const response = await fetch(`${apiUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Registration failed');
    }

    const data: AuthResponse = await response.json();
    setAuth(data);
    return data;
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
}

/**
 * Refresh access token using refresh token
 */
export async function refreshAccessToken(): Promise<string> {
  try {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${apiUrl}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearAuth();
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    setStorageItem(ACCESS_TOKEN_KEY, data.access_token);

    return data.access_token;
  } catch (error) {
    console.error('Token refresh error:', error);
    clearAuth();
    throw error;
  }
}

/**
 * Request password reset
 */
export async function requestPasswordReset(email: string): Promise<{ message: string }> {
  try {
    const response = await fetch(`${apiUrl}/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Password reset request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Password reset error:', error);
    throw error;
  }
}

/**
 * Reset password with token
 */
export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ message: string }> {
  try {
    const response = await fetch(`${apiUrl}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token,
        new_password: newPassword,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Password reset failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Reset password error:', error);
    throw error;
  }
}

/**
 * Verify token is still valid
 */
export async function verifyToken(): Promise<boolean> {
  try {
    const token = getAccessToken();
    if (!token) return false;

    const response = await fetch(`${apiUrl}/auth/verify`, {
      method: 'GET',
      headers: {
        ...getAuthHeader(),
      },
    });

    return response.ok;
  } catch (error) {
    console.error('Token verification error:', error);
    return false;
  }
}

/**
 * Check if JWT token is expired
 */
export function isTokenExpired(): boolean {
  const token = getAccessToken();
  if (!token) return true;

  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;

    const payload = JSON.parse(atob(parts[1]));
    const expTime = payload.exp * 1000;
    return Date.now() >= expTime;
  } catch {
    return true;
  }
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    const token = getAccessToken();
    if (token) {
      await fetch(`${apiUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
      });
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearAuth();
  }
}
