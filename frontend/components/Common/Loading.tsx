'use client';

export interface LoadingProps {
  message?: string;
  fullscreen?: boolean;
}

export function Loading({ message = 'Loading...', fullscreen = false }: LoadingProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-transparent border-t-brand-primary border-r-brand-primary rounded-full animate-spin"></div>
      </div>
      {message && <p className="text-slate-600 font-medium">{message}</p>}
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-12">
      {content}
    </div>
  );
}

export function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="animate-pulse">
          <div className="h-20 bg-slate-200 rounded-lg"></div>
        </div>
      ))}
    </div>
  );
}
