'use client';

import React from 'react';
import Link from 'next/link';

export interface ConversationItem {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
}

interface ConversationHistoryProps {
  conversations: ConversationItem[];
  currentId?: string;
  onSelect?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export function ConversationHistory({
  conversations,
  currentId,
  onSelect,
  onDelete,
}: ConversationHistoryProps) {
  return (
    <div className="w-full md:w-64 bg-slate-100 border-r border-slate-300 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-300">
        <Link
          href="/chat/new"
          className="w-full bg-medical-primary text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-center block font-medium"
        >
          + New Chat
        </Link>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-slate-500 text-sm">
            <p>No conversations yet</p>
            <p className="mt-2">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="space-y-2 p-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`p-3 rounded-lg cursor-pointer transition-colors group ${
                  currentId === conv.id
                    ? 'bg-medical-primary text-white'
                    : 'bg-white hover:bg-slate-200 text-slate-900'
                }`}
                onClick={() => onSelect?.(conv.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate text-sm">{conv.title}</h4>
                    <p className={`text-xs truncate ${currentId === conv.id ? 'text-blue-100' : 'text-slate-500'}`}>
                      {conv.lastMessage}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete?.(conv.id);
                    }}
                    className={`ml-2 opacity-0 group-hover:opacity-100 transition-opacity ${
                      currentId === conv.id ? 'hover:text-red-200' : 'hover:text-red-600'
                    }`}
                    title="Delete conversation"
                  >
                    ✕
                  </button>
                </div>
                <p className={`text-xs mt-1 ${currentId === conv.id ? 'text-blue-100' : 'text-slate-400'}`}>
                  {conv.messageCount} messages
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer with info */}
      <div className="p-3 border-t border-slate-300 text-xs text-slate-500 text-center">
        <p>Chat history is saved locally</p>
      </div>
    </div>
  );
}
