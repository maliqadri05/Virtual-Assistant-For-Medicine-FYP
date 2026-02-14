'use client';

import React from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  loading?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timeString = message.timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-medical-primary text-white rounded-br-none'
            : 'bg-slate-200 text-slate-900 rounded-bl-none'
        }`}
      >
        <div className="break-words">
          {message.loading ? (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-current rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
          ) : (
            <p>{message.content}</p>
          )}
        </div>
        <p className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-slate-500'}`}>
          {timeString}
        </p>
      </div>
    </div>
  );
}
