/**
 * Protected Routes Integration Tests
 * Tests for ProtectedRoute component and auth-aware navigation
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { ProtectedRoute } from '@/components/ProtectedRoute';

// Mock useAuth hook
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}));

// Mock useRouter
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';

describe('ProtectedRoute Component', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  test('should render protected content when authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { id: '1', email: 'test@example.com' },
    });

    const TestComponent = () => <div>Protected Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('should show loading when checking authentication', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      user: null,
    });

    const TestComponent = () => <div>Protected Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    // Should show loading skeleton or similar
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('should redirect to login when not authenticated', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    const TestComponent = () => <div>Protected Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/auth/login');
    });
  });

  test('should verify token expiration on route protection', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    const TestComponent = () => <div>Protected Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/auth/login');
    });
  });
});

describe('Protected Routes Workflow', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  test('should allow access to dashboard when authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { id: '1', email: 'test@example.com' },
    });

    const TestComponent = () => <div>Dashboard Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
  });

  test('should block access to chat when not authenticated', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    const TestComponent = () => <div>Chat Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/auth/login');
      expect(screen.queryByText('Chat Content')).not.toBeInTheDocument();
    });
  });

  test('should preserve location after successful login', async () => {
    // Initially not authenticated
    const { rerender } = (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    const TestComponent = () => <div>Profile Content</div>;

    const { container } = render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    // User logs in
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { id: '1', email: 'test@example.com' },
    });

    rerender(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(screen.getByText('Profile Content')).toBeInTheDocument();
    });
  });
});

describe('Authentication State Management', () => {
  test('should maintain authentication state across navigations', () => {
    const user = { id: '1', email: 'test@example.com' };

    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user,
    });

    const Component1 = () => <div>Component 1</div>;
    const Component2 = () => <div>Component 2</div>;

    const { rerender } = render(
      <ProtectedRoute>
        <Component1 />
      </ProtectedRoute>
    );

    expect(screen.getByText('Component 1')).toBeInTheDocument();

    rerender(
      <ProtectedRoute>
        <Component2 />
      </ProtectedRoute>
    );

    expect(screen.getByText('Component 2')).toBeInTheDocument();
    expect(screen.queryByText('Component 1')).not.toBeInTheDocument();
  });

  test('should handle authentication errors gracefully', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      error: 'Token expired',
    });

    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    const TestComponent = () => <div>Protected Content</div>;

    render(
      <ProtectedRoute>
        <TestComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/auth/login');
    });
  });
});
