'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { LoadingSkeleton } from '@/components/Common/Loading';
import { ErrorAlert } from '@/components/Common/Error';

interface ReportSummary {
  id: string;
  title: string;
  createdAt: Date;
  conversationId: string;
  diagnosis: string;
}

export default function ReportsListPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true);
        setError(null);
        // Mock reports - in real app this would call API
        const mockReports: ReportSummary[] = [
          {
            id: 'report-001',
            title: 'Medical Consultation Report',
            createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
            conversationId: 'conv-001',
            diagnosis: 'Suspected viral pharyngitis',
          },
          {
            id: 'report-002',
            title: 'Follow-up Consultation',
            createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            conversationId: 'conv-002',
            diagnosis: 'Migraine headache management',
          },
        ];
        setReports(mockReports);
      } catch (err) {
        setError('Failed to load reports');
        console.error('Error loading reports:', err);
      } finally {
        setLoading(false);
      }
    };

    loadReports();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-medical-primary text-white">
        <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Medical Reports</h1>
              <p className="text-blue-100 mt-2">Your generated reports and documents</p>
            </div>
            <Link
              href="/chat/new"
              className="bg-white text-medical-primary hover:bg-blue-50 font-bold py-2 px-6 rounded-lg transition-colors"
            >
              + New Consultation
            </Link>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="mb-6">
            <ErrorAlert
              title="Error Loading Reports"
              message={error}
              onRetry={() => window.location.reload()}
            />
          </div>
        )}

        {loading && <LoadingSkeleton />}

        {!loading && reports.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">No Reports Yet</h2>
            <p className="text-slate-600 max-w-md mx-auto">
              Start a consultation to generate your first medical report.
            </p>
            <Link
              href="/chat/new"
              className="inline-block mt-6 bg-medical-primary text-white font-medium py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Consultation
            </Link>
          </div>
        )}

        {!loading && reports.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {reports.map((report) => (
              <Link
                key={report.id}
                href={`/reports/${report.id}`}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-slate-100 hover:border-medical-primary cursor-pointer"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {report.title}
                    </h3>
                    <p className="text-sm text-slate-500">
                      {report.createdAt.toLocaleDateString()}
                    </p>
                  </div>
                  <span className="text-2xl">📄</span>
                </div>

                <p className="text-slate-600 mb-4">
                  <strong>Diagnosis:</strong> {report.diagnosis}
                </p>

                <div className="flex gap-2">
                  <button className="flex-1 bg-medical-primary hover:bg-blue-700 text-white px-4 py-2 rounded font-medium transition-colors">
                    View Report
                  </button>
                  <button className="flex-1 bg-slate-200 hover:bg-slate-300 text-slate-900 px-4 py-2 rounded font-medium transition-colors">
                    Share
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
