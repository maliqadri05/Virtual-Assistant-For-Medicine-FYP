'use client';

import React, { useRef, useState } from 'react';
import { ReportSection as ReportSectionComp, ReportSection as ReportSectionType } from './ReportSection';

export interface ReportData {
  id: string;
  conversationId: string;
  title: string;
  generatedAt: Date;
  symptoms: string[];
  findings: string;
  recommendations: string[];
  diagnosis: string;
  disclaimer: string;
  metadata?: {
    doctorName?: string;
    hospitalName?: string;
    consultationDuration?: number;
  };
}

interface ReportDisplayProps {
  report: ReportData;
  onClose?: () => void;
  showActions?: boolean;
}

export function ReportDisplay({
  report,
  onClose,
  showActions = true,
}: ReportDisplayProps) {
  const reportRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);

  const sections: ReportSectionType[] = [
    {
      title: 'Patient Symptoms',
      content: report.symptoms.join('\n• '),
      type: 'symptoms',
    },
    {
      title: 'Medical Findings',
      content: report.findings,
      type: 'findings',
    },
    {
      title: 'Diagnosis',
      content: report.diagnosis,
      type: 'diagnostic',
    },
    {
      title: 'Recommendations',
      content: report.recommendations.join('\n• '),
      type: 'recommendations',
    },
  ];

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: report.title,
        text: `Medical Report: ${report.title}\n\n${report.findings}`,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(
        `${report.title}\n\n${report.findings}\n\n${report.recommendations.join('\n')}`
      );
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadJSON = () => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${report.id}.json`;
    link.click();
  };

  const handleCopyToClipboard = () => {
    const fullText = `
${report.title}

Generated: ${report.generatedAt.toLocaleString()}

SYMPTOMS:
${report.symptoms.map((s) => `• ${s}`).join('\n')}

FINDINGS:
${report.findings}

DIAGNOSIS:
${report.diagnosis}

RECOMMENDATIONS:
${report.recommendations.map((r) => `• ${r}`).join('\n')}

DISCLAIMER:
${report.disclaimer}
    `.trim();

    navigator.clipboard.writeText(fullText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-medical-primary text-white p-6 print:bg-slate-900">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{report.title}</h1>
            <p className="text-blue-100">
              Generated on {report.generatedAt.toLocaleDateString()} at{' '}
              {report.generatedAt.toLocaleTimeString()}
            </p>
            {report.metadata?.doctorName && (
              <p className="text-blue-100 text-sm mt-2">
                By: Dr. {report.metadata.doctorName}
              </p>
            )}
          </div>
          {showActions && (
            <button
              onClick={onClose}
              className="text-2xl font-bold hover:text-blue-200 transition-colors print:hidden"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div
        ref={reportRef}
        className="p-8 max-w-4xl mx-auto print:p-0 print:max-w-full"
      >
        {/* Symptoms */}
        {sections.map((section, idx) => (
          <ReportSectionComp
            key={idx}
            section={section}
          />
        ))}

        {/* Disclaimer */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg mt-8">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">
            ⚠️ Important Medical Disclaimer
          </h3>
          <p className="text-sm text-yellow-800">{report.disclaimer}</p>
        </div>

        {/* Metadata */}
        {report.metadata && (
          <div className="mt-8 pt-6 border-t border-slate-200 text-xs text-slate-500 print:hidden">
            <p>Report ID: {report.id}</p>
            <p>
              Consultation Duration:{' '}
              {report.metadata.consultationDuration
                ? `${Math.round(report.metadata.consultationDuration / 60)} minutes`
                : 'N/A'}
            </p>
          </div>
        )}
      </div>

      {/* Actions Footer */}
      {showActions && (
        <div className="bg-slate-50 border-t border-slate-200 p-6 flex gap-3 flex-wrap print:hidden">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 bg-medical-primary hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            title="Print report (Ctrl+P)"
          >
            🖨️ Print
          </button>
          <button
            onClick={handleDownloadJSON}
            className="flex items-center gap-2 bg-slate-600 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            title="Download as JSON"
          >
            📥 Download JSON
          </button>
          <button
            onClick={handleCopyToClipboard}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              copied
                ? 'bg-green-500 text-white'
                : 'bg-slate-300 hover:bg-slate-400 text-slate-900'
            }`}
            title="Copy entire report to clipboard"
          >
            {copied ? '✓ Copied' : '📋 Copy Full'}
          </button>
          <button
            onClick={handleShare}
            className="flex items-center gap-2 bg-slate-500 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-medium transition-colors ml-auto"
            title="Share report"
          >
            🔗 Share
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="flex items-center gap-2 bg-slate-300 hover:bg-slate-400 text-slate-900 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Close
            </button>
          )}
        </div>
      )}

      {/* Print Styles */}
      <style>{`
        @media print {
          body {
            margin: 0;
            padding: 0;
          }
          .print\\:hidden {
            display: none !important;
          }
          .print\\:bg-slate-900 {
            background-color: #111827 !important;
          }
        }
      `}</style>
    </div>
  );
}
