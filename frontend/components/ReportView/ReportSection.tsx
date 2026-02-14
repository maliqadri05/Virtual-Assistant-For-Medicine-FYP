'use client';

import React, { useRef } from 'react';

export interface ReportSection {
  title: string;
  content: string;
  type: 'findings' | 'recommendations' | 'symptoms' | 'diagnostic' | 'custom';
}

interface ReportSectionProps {
  section: ReportSection;
}

export function ReportSection({ section }: ReportSectionProps) {
  const [copied, setCopied] = React.useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleCopy = () => {
    const text = contentRef.current?.innerText || '';
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const getSectionColor = () => {
    switch (section.type) {
      case 'findings':
        return 'border-medical-primary bg-blue-50';
      case 'recommendations':
        return 'border-medical-success bg-green-50';
      case 'symptoms':
        return 'border-medical-info bg-cyan-50';
      case 'diagnostic':
        return 'border-yellow-400 bg-yellow-50';
      default:
        return 'border-slate-300 bg-slate-50';
    }
  };

  const getSectionIcon = () => {
    switch (section.type) {
      case 'findings':
        return '🔍';
      case 'recommendations':
        return '✅';
      case 'symptoms':
        return '🩺';
      case 'diagnostic':
        return '⚕️';
      default:
        return '📋';
    }
  };

  return (
    <div className={`border-l-4 rounded-lg p-6 mb-6 ${getSectionColor()}`}>
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
          <span>{getSectionIcon()}</span>
          {section.title}
        </h3>
        <button
          onClick={handleCopy}
          className={`px-3 py-1 rounded text-sm font-medium transition-all ${
            copied
              ? 'bg-green-500 text-white'
              : 'bg-slate-200 hover:bg-slate-300 text-slate-700'
          }`}
          title="Copy section to clipboard"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>
      <div
        ref={contentRef}
        className="text-slate-700 whitespace-pre-wrap leading-relaxed prose prose-sm max-w-none"
      >
        {section.content}
      </div>
    </div>
  );
}
