// Authentication utilities
import { authAPI } from './api';
import { setStorageItem, getStorageItem, removeStorageItem } from '@/services/storage';

const AUTH_TOKEN_KEY = 'auth_token';
const USER_KEY = 'user';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!getStorageItem(AUTH_TOKEN_KEY);
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
 * Get auth token
 */
export function getToken(): string | null {
  return getStorageItem(AUTH_TOKEN_KEY);
}

/**
 * Save auth token and user
 */
export function setAuth(token: string, user: User): void {
  setStorageItem(AUTH_TOKEN_KEY, token);
  setStorageItem(USER_KEY, JSON.stringify(user));
}

/**
 * Clear authentication
 */
export function clearAuth(): void {
  removeStorageItem(AUTH_TOKEN_KEY);
  removeStorageItem(USER_KEY);
}

/**
 * Login user
 */
export async function login(email: string, password: string): Promise<User> {
  try {
    const response = await authAPI.login(email, password);
    const user: User = {
      id: email,
      email,
      name: email.split('@')[0],
    };
    setAuth(response.token, user);
    return user;
  } catch (error) {
    clearAuth();
    throw new Error('Login failed: Invalid credentials');
  }
}

/**
 * Logout user
 */
export function logout(): void {
  clearAuth();
  authAPI.logout();
}

/**
 * Register new user
 */
export async function register(
  email: string,
  password: string,
  name: string
): Promise<User> {
  try {
    await authAPI.register(email, password, name);
    return await login(email, password);
  } catch (error) {
    throw new Error('Registration failed');
  }
}

/**
 * Refresh authentication token
 */
export async function refreshAuth(): Promise<string> {
  try {
    const response = await authAPI.refreshToken();
    const user = getCurrentUser();
    if (user) {
      setAuth(response.token, user);
    }
    return response.token;
  } catch (error) {
    clearAuth();
    throw new Error('Token refresh failed');
  }
}

/**
 * Check token expiration
 */
export function isTokenExpired(): boolean {
  const token = getToken();
  if (!token) return true;

  try {
    // Decode JWT token (simple decoding without verification)
    const parts = token.split('.');
    if (parts.length !== 3) return true;

    const payload = JSON.parse(atob(parts[1]));
    const expTime = payload.exp * 1000;
    return Date.now() >= expTime;
  } catch {
    return true;
  }
}
