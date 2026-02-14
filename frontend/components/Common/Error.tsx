'use client';

export interface ErrorProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  fullscreen?: boolean;
}

export function ErrorAlert({
  title = 'Error',
  message,
  onRetry,
  fullscreen = false,
}: ErrorProps) {
  const content = (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <p className="mt-2 text-sm text-red-700">{message}</p>
          {onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center p-4 z-50">
        <div className="max-w-md w-full">{content}</div>
      </div>
    );
  }

  return content;
}

export function ErrorBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  // Note: For production, use a proper error boundary library
  // This is a basic implementation
  return <>{children}</>;
}
