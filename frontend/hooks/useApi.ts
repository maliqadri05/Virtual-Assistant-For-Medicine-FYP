/**
 * useAPI Hook
 * Custom React hook for making API calls with built-in loading, error, and data state management
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import apiService, { RequestOptions } from '@/services/api';

/**
 * API State
 */
export interface UseAPIState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  isRefetching: boolean;
}

/**
 * useAPI Hook Options
 */
interface UseAPIOptions extends Omit<RequestOptions, 'method' | 'body'> {
  autoFetch?: boolean;
  dependencies?: any[];
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

/**
 * useAPI - GET request hook
 */
export function useAPI<T = any>(
  endpoint: string | null,
  options: UseAPIOptions = {}
): UseAPIState<T> {
  const {
    autoFetch = true,
    dependencies = [],
    onSuccess,
    onError,
    ...requestOptions
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(autoFetch && !!endpoint);
  const [error, setError] = useState<Error | null>(null);
  const [isRefetching, setIsRefetching] = useState(false);

  const fetch = useCallback(async () => {
    if (!endpoint) {
      setData(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await apiService.get<T>(endpoint, {
        ...requestOptions,
        timeout: requestOptions.timeout || 30000,
      });

      setData(result);
      onSuccess?.(result);
    } catch (err: any) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [endpoint, requestOptions, onSuccess, onError]);

  const refetch = useCallback(async () => {
    setIsRefetching(true);
    try {
      await fetch();
    } finally {
      setIsRefetching(false);
    }
  }, [fetch]);

  useEffect(() => {
    if (autoFetch && endpoint) {
      fetch();
    }
  }, [endpoint, autoFetch, fetch]);

  return { data, loading, error, refetch, isRefetching };
}

/**
 * useMutation Hook - POST/PUT/DELETE request hook
 */
export interface UseMutationOptions<TResponse> extends Omit<RequestOptions, 'body'> {
  onSuccess?: (data: TResponse) => void;
  onError?: (error: Error) => void;
}

export interface UseMutationState<TResponse> {
  mutate: (body?: any) => Promise<TResponse>;
  mutateAsync: (body?: any) => Promise<TResponse>;
  isLoading: boolean;
  error: Error | null;
  data: TResponse | null;
  reset: () => void;
}

/**
 * useMutation - Custom hook for mutations
 */
export function useMutation<TResponse = any>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
  options: UseMutationOptions<TResponse> = {}
): UseMutationState<TResponse> {
  const { onSuccess, onError, ...requestOptions } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<TResponse | null>(null);

  const mutateAsync = useCallback(
    async (body?: any): Promise<TResponse> => {
      try {
        setIsLoading(true);
        setError(null);

        let result: TResponse;

        switch (method) {
          case 'POST':
            result = await apiService.post<TResponse>(endpoint, body, requestOptions);
            break;
          case 'PUT':
            result = await apiService.put<TResponse>(endpoint, body, requestOptions);
            break;
          case 'PATCH':
            result = await apiService.patch<TResponse>(endpoint, body, requestOptions);
            break;
          case 'DELETE':
            result = await apiService.delete<TResponse>(endpoint, requestOptions);
            break;
          default:
            throw new Error(`Unsupported method: ${method}`);
        }

        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err: any) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        onError?.(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [endpoint, method, requestOptions, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    mutate: (body?: any) => mutateAsync(body),
    mutateAsync,
    isLoading,
    error,
    data,
    reset,
  };
}

// eslint-disable-next-line react-hooks/exhaustive-deps
/**
 * usePaginatedAPI - Hook for paginated API requests
 */
export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface UsePaginatedAPIState<T> extends UseAPIState<T[]> {
  pagination: PaginationState;
  nextPage: () => void;
  previousPage: () => void;
  goToPage: (page: number) => void;
  setPageSize: (size: number) => void;
}

/**
 * usePaginatedAPI - Hook for paginated requests
 */
export function usePaginatedAPI<T = any>(
  endpoint: string,
  options: UseAPIOptions & { pageSize?: number } = {}
): UsePaginatedAPIState<T> {
  const { pageSize: initialPageSize = 20, ...apiOptions } = options;

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [total, setTotal] = useState(0);

  const { data: rawData, loading, error, refetch: baseRefetch } = useAPI<any>(
    `${endpoint}?skip=${(page - 1) * pageSize}&limit=${pageSize}`,
    { ...apiOptions, autoFetch: true, dependencies: [page, pageSize] }
  );

  const data = rawData?.items || rawData?.data || [];
  const total_ = rawData?.total || total;
  const hasNextPage = page * pageSize < total_;
  const hasPreviousPage = page > 1;

  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setPage((p) => p + 1);
    }
  }, [hasNextPage]);

  const previousPage = useCallback(() => {
    if (hasPreviousPage) {
      setPage((p) => p - 1);
    }
  }, [hasPreviousPage]);

  const goToPage = useCallback((newPage: number) => {
    if (newPage > 0) {
      setPage(newPage);
    }
  }, []);

  const refetch = useCallback(() => {
    setPage(1);
    baseRefetch();
  }, [baseRefetch]);

  useEffect(() => {
    if (rawData?.total) {
      setTotal(rawData.total);
    }
  }, [rawData?.total]);

  return {
    data: data as T[],
    loading,
    error,
    refetch,
    isRefetching: false,
    pagination: {
      page,
      pageSize,
      total: total_,
      hasNextPage,
      hasPreviousPage,
    },
    nextPage,
    previousPage,
    goToPage,
    setPageSize,
  };
}

/**
 * useApiInterceptor - Hook to add custom interceptors
 */
export function useApiInterceptor(
  interceptor: 'request' | 'response' | 'error',
  handler: any
): void {
  useEffect(() => {
    const interceptors = apiService.getInterceptors();

    switch (interceptor) {
      case 'request':
        interceptors.addRequestInterceptor(handler);
        break;
      case 'response':
        interceptors.addResponseInterceptor(handler);
        break;
      case 'error':
        interceptors.addErrorInterceptor(handler);
        break;
    }
  }, [interceptor, handler]);
}
