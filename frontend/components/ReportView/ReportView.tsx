'use client';

import React from 'react';

export interface ReportData {
  id: string;
  conversationId: string;
  title: string;
  generatedAt: Date;
  symptoms: string[];
  findings: string;
  recommendations: string[];
  disclaimer: string;
}

interface ReportViewProps {
  report: ReportData;
  onExport?: (format: 'pdf' | 'txt') => void;
  onClose?: () => void;
}

export function ReportView({ report, onExport, onClose }: ReportViewProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{report.title}</h2>
          <p className="text-sm text-slate-500 mt-1">
            Generated on {report.generatedAt.toLocaleDateString()} at{' '}
            {report.generatedAt.toLocaleTimeString()}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 text-2xl font-bold"
        >
          ✕
        </button>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Symptoms */}
        {report.symptoms.length > 0 && (
          <section className="border-b border-slate-200 pb-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Symptoms</h3>
            <ul className="list-disc list-inside space-y-2">
              {report.symptoms.map((symptom, idx) => (
                <li key={idx} className="text-slate-700">
                  {symptom}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Findings */}
        <section className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">Medical Findings</h3>
          <div className="bg-blue-50 border-l-4 border-medical-primary p-4 rounded">
            <p className="text-slate-700 whitespace-pre-wrap">{report.findings}</p>
          </div>
        </section>

        {/* Recommendations */}
        {report.recommendations.length > 0 && (
          <section className="border-b border-slate-200 pb-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Recommendations</h3>
            <ol className="list-decimal list-inside space-y-2">
              {report.recommendations.map((rec, idx) => (
                <li key={idx} className="text-slate-700">
                  {rec}
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Disclaimer */}
        <section className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">⚠️ Important Disclaimer</h3>
          <p className="text-sm text-yellow-800">{report.disclaimer}</p>
        </section>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mt-8 pt-6 border-t border-slate-200">
        <button
          onClick={() => onExport?.('pdf')}
          className="flex-1 bg-medical-primary hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          📥 Download PDF
        </button>
        <button
          onClick={() => onExport?.('txt')}
          className="flex-1 bg-slate-300 hover:bg-slate-400 text-slate-900 font-medium py-2 px-4 rounded-lg transition-colors"
        >
          📄 Download Text
        </button>
        <button
          onClick={onClose}
          className="flex-1 bg-slate-200 hover:bg-slate-300 text-slate-900 font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
