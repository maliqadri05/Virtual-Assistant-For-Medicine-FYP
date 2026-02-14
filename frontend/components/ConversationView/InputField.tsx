'use client';

import React, { useState, useRef, useEffect } from 'react';

interface InputFieldProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function InputField({
  onSubmit,
  disabled = false,
  placeholder = 'Type your message...',
}: InputFieldProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea with content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, 120) + 'px';
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSubmit(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (Shift+Enter for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end px-4 py-3 bg-white border-t border-slate-200">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className={`flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-medical-primary resize-none transition-colors ${
          disabled ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-white'
        }`}
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
          disabled || !input.trim()
            ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
            : 'bg-medical-primary text-white hover:bg-blue-700 active:bg-blue-800'
        }`}
        title={disabled ? 'Loading...' : input.trim() ? 'Send message (Enter)' : 'Type a message first'}
      >
        {disabled ? (
          <span className="inline-block">
            <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </span>
        ) : (
          <span>Send</span>
        )}
      </button>
    </form>
  );
}
